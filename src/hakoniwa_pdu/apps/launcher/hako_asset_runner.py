# launcher/hako_launch/hako_asset_runner.py
from __future__ import annotations

import os, sys, time, signal, subprocess, json
from dataclasses import dataclass
from typing import Mapping, Optional, Iterable, Union
from os import PathLike
import re

IS_POSIX = (os.name == "posix")
IS_WIN   = (os.name == "nt")

PathStr = Union[str, PathLike[str]]

def _ps_quote(s: str) -> str:
    return "'" + s.replace("'", "''") + "'"

def _is_wsl() -> bool:
    try:
        with open("/proc/version", "r", errors="ignore") as f:
            ver = f.read()
    except Exception:
        ver = ""
    return bool(os.getenv("WSL_INTEROP")) or os.path.exists("/proc/sys/fs/binfmt_misc/WSLInterop") \
           or ("Microsoft" in ver)


def _looks_windows_exe(cmd: str) -> bool:
    c = cmd.lower()
    return c.endswith(".exe") or c in ("cmd.exe", "powershell.exe")

def _to_windows_path(p: Optional[PathStr], *, cwd: Optional[PathStr]) -> Optional[str]:
    if p is None:
        return None
    # 絶対化（cwd は WSL側のパス想定）
    p = os.path.abspath(os.fspath(p) if cwd is None else os.path.join(os.fspath(cwd), os.fspath(p)))
    try:
        # wslpath -w で Windows パスへ
        out = subprocess.check_output(["wslpath", "-w", p], text=True).strip()
        return out
    except Exception:
        # /mnt/c/... ならそのままでも通る場合アリ。最悪は無変換で返す。
        return p

TASKLIST = r"/mnt/c/Windows/System32/tasklist.exe"
def _win_pid_exists(pid: int) -> bool:
    try:
        cp = subprocess.run(
            [TASKLIST, "/FO", "CSV", "/NH", "/FI", f"PID eq {pid}"],
            text=True,
            stderr=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            timeout=2.0,
            check=False,
        )
        out = (cp.stdout or "").strip()
        # 例: "notepad.exe","12345","Console","1","12,345 K"
        if not out or out[0] != '"':
            return False
        try:
            return f',"{pid}",' in out
        except Exception:
            return False
    except subprocess.TimeoutExpired:
        # タイムアウト時は存続とみなす（誤検知防止）
        return True
    except Exception:
        return False

@dataclass
class ExitInfo:
    exited: bool
    exit_code: Optional[int] = None
    signal: Optional[int] = None
    started_at: float = 0.0
    exited_at: Optional[float] = None
    pid: Optional[int] = None

@dataclass
class ProcHandle:
    popen: subprocess.Popen
    started_at: float
    stdout_path: Optional[str] = None
    stderr_path: Optional[str] = None
    _stdout_f: Optional[object] = None   # 後で close するため保持
    _stderr_f: Optional[object] = None

class AssetRunner:
    """単一アセット（=1 OSプロセス）のライフサイクルを扱う最小クラス。"""

    def __init__(self, *, env: Optional[Mapping[str, str]] = None) -> None:
        # envmerge 済みの環境を受け取り、親環境とマージ済み前提（そのまま渡す）
        self.env = dict(os.environ) | dict(env or {})
        self.handle: Optional[ProcHandle] = None
        self._win_pid: Optional[int] = None

    # ---------- helpers ----------
    @staticmethod
    def _open_sink(path: Optional[PathStr]):
        if path is None:
            return None, None
        path = os.fspath(path)
        parent = os.path.dirname(path)
        if parent:  # "" のとき mkdir しない
            os.makedirs(parent, exist_ok=True)
        # バイナリ新規作成・バッファリング無しで落とす
        f = open(path, "wb", buffering=0)
        return f, path

    @staticmethod
    def _creationflags() -> int:
        if IS_WIN:
            # CTRL_BREAK を送るには NEW_PROCESS_GROUP が必要
            return getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)  # type: ignore[attr-defined]
        return 0

    # ---------- lifecycle ----------
    def spawn(
        self,
        command: str,
        args: Iterable[str] = (),
        *,
        cwd: Optional[PathStr] = None,
        stdout: Optional[PathStr] = None,
        stderr: Optional[PathStr] = None,
    ) -> ProcHandle:
        if self.handle and self.is_alive():
            raise RuntimeError("process already running")

        # --- Windows(.exe) を WSL から起動する分岐（本体は Windows プロセス） ---
        if _is_wsl() and _looks_windows_exe(command):
            win_out = _to_windows_path(stdout, cwd=cwd)
            win_err = _to_windows_path(stderr, cwd=cwd)
            win_cwd = _to_windows_path(cwd, cwd=None) if cwd else None

            # 親ディレクトリ作成（Windows側で）
            pre = []
            if win_out:
                pre.append(f"[System.IO.Directory]::CreateDirectory((Split-Path {_ps_quote(win_out)})) | Out-Null;")
            if win_err:
                pre.append(f"[System.IO.Directory]::CreateDirectory((Split-Path {_ps_quote(win_err)})) | Out-Null;")
            pre_cmd = "".join(pre)

            # 引数組み立て
            exe_name = os.fspath(command)              # 例: "simulation.exe"
            exe_quoted = _ps_quote(exe_name)
            arg_elems = ",".join(_ps_quote(str(a)) for a in list(args))
            arglist = (f"-ArgumentList {arg_elems} " if arg_elems else "")

            redir_out = f" -RedirectStandardOutput {_ps_quote(win_out)} " if win_out else ""
            redir_err = f" -RedirectStandardError {_ps_quote(win_err)} " if win_err else ""
            wd = f" -WorkingDirectory {_ps_quote(win_cwd)} " if win_cwd else ""

            ps_script = (
                "[Console]::OutputEncoding=[System.Text.Encoding]::UTF8; "
                "$ErrorActionPreference='Stop'; "
                f"{'Set-Location ' + _ps_quote(_to_windows_path(cwd, cwd=None)) + '; ' if cwd else ''}"
                # ★ FilePath/WorkingDirectory/リダイレクト/WindowStyle は使わない
                f"$p = Start-Process {exe_quoted}{arglist} -PassThru; "
                "$p | Select-Object -ExpandProperty Id"
            )
            #print(f"[INFO] ps_script={ps_script}")
            #print(f"[INFO] win_cwd={win_cwd}, command={exe_name}, args={list(args)}")

            pwsh = [
                "powershell.exe", "-NoProfile", "-NonInteractive",
                "-ExecutionPolicy", "Bypass", "-Command", ps_script
            ]
            out = subprocess.check_output(
                pwsh,
                # PowerShell 自体の cwd は WSL パスでもOKだが、無指定が一番トラブル少ない
                cwd=None,
                # ★ 重要：WSL 環境変数を渡さない（Windows PATH を壊さない）
                env=None,
                text=True,
                encoding="utf-8",
                stderr=subprocess.PIPE,
                timeout=15.0
            )
            self._win_pid = int(out.strip())
            dummy = subprocess.Popen(["/bin/true"]) if IS_POSIX else subprocess.Popen(["cmd.exe", "/c", "exit", "0"])
            self.handle = ProcHandle(
                popen=dummy,
                started_at=time.time(),
                stdout_path=(os.fspath(stdout) if stdout else None),
                stderr_path=(os.fspath(stderr) if stderr else None),
                _stdout_f=None, _stderr_f=None
            )
            return self.handle

        # --- Mac/Linux/WSL ネイティブプロセス ---
        out_f, out_path = self._open_sink(stdout)
        err_f, err_path = self._open_sink(stderr)

        popen_kw: dict = dict(
            cwd=(os.fspath(cwd) if cwd is not None else None),
            env=self.env,
            stdout=(out_f or None),
            stderr=(err_f or None),
            creationflags=self._creationflags(),
            close_fds=True,
        )
        if IS_POSIX:
            popen_kw["preexec_fn"] = os.setsid

        popen = subprocess.Popen([command, *list(args)], **popen_kw)

        self.handle = ProcHandle(
            popen=popen,
            started_at=time.time(),
            stdout_path=(out_path or None),
            stderr_path=(err_path or None),
            _stdout_f=out_f,
            _stderr_f=err_f,
        )
        return self.handle
    
    

    def is_alive(self) -> bool:
        if self._win_pid is not None:
            return _win_pid_exists(self._win_pid)
        return bool(self.handle) and self.handle.popen.poll() is None

    def wait(self, *, timeout: Optional[float] = None) -> Optional[int]:
        if self._win_pid is not None:
            end = None if timeout is None else (time.time() + float(timeout))
            while True:
                if not self.is_alive():
                    return 0
                if end is not None and time.time() >= end:
                    return None
                time.sleep(0.1)
        if not self.handle:
            return 0
        try:
            return self.handle.popen.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            return None


    def terminate(self, *, grace_sec: float = 5.0) -> None:
        """優雅停止（TERM/CTRL_BREAK）→ 猶予 → 未終了なら kill()。"""
        h = self.handle
        # Windows プロセス（.exe）を WSL から管理する場合
        if self._win_pid is not None:
            ps_script = f"""
                $ErrorActionPreference='SilentlyContinue'
                try {{
                $p = Get-Process -Id {self._win_pid} -ErrorAction Stop
                if ($p.MainWindowHandle -ne 0) {{ $null = $p.CloseMainWindow(); Wait-Process -Id {self._win_pid} -Timeout {max(1,int(grace_sec//2))} -ErrorAction SilentlyContinue }}
                }} catch {{ }}
                Stop-Process -Id {self._win_pid} -ErrorAction SilentlyContinue
                exit 0
                """
            subprocess.run(
                ["powershell.exe", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=max(3.0, grace_sec)
            )
            self._wait_for_exit(timeout=grace_sec)
            if self.is_alive():
                self.kill()
            else:
                self._win_pid = None
                self._cleanup_files()
            return

        if not h or not self.is_alive():
            self._cleanup_files()
            return
        try:
            if IS_POSIX:
                os.killpg(h.popen.pid, signal.SIGTERM)  # type: ignore[arg-type]
            elif IS_WIN:
                h.popen.send_signal(getattr(signal, "CTRL_BREAK_EVENT", signal.SIGTERM))  # type: ignore[attr-defined]
            else:
                h.popen.terminate()
        except Exception:
            self.kill()
            return

        self._wait_for_exit(timeout=grace_sec)
        if self.is_alive():
            self.kill()
        else:
            self._cleanup_files()

        self._wait_for_exit(timeout=grace_sec)
        if self.is_alive():
            self.kill()
        else:
            self._cleanup_files()

    def kill(self) -> None:
        # Windows 側 PID を掴んでいる場合は強制終了
        if self._win_pid is not None:
            subprocess.run(
                ["taskkill.exe", "/PID", str(self._win_pid), "/T", "/F"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5.0
            )
            self._wait_for_exit(timeout=2.0)
            self._win_pid = None
            self._cleanup_files()
            return

        h = self.handle
        if not h or not self.is_alive():
            self._cleanup_files()
            return
        try:
            if IS_POSIX:
                os.killpg(h.popen.pid, signal.SIGKILL)  # type: ignore[arg-type]
            else:
                h.popen.kill()
        finally:
            self._wait_for_exit(timeout=2.0)
            self._cleanup_files()

    def exit_info(self) -> ExitInfo:
        h = self.handle
        # Windows プロセス優先で情報を埋める
        if self._win_pid is not None:
            alive = self.is_alive()
            return ExitInfo(
                exited=(not alive),
                exit_code=None,  # 取得は面倒なので None（必要なら Get-Process の HasExited 等の追加実装へ）
                signal=None,
                started_at=(h.started_at if h else 0.0),
                exited_at=(time.time() if not alive else None),
                pid=self._win_pid
            )
                
        if not h:
            return ExitInfo(exited=True, exit_code=None, signal=None, started_at=0.0, exited_at=time.time(), pid=None)

        rc = h.popen.poll()
        info = ExitInfo(
            exited=(rc is not None),
            started_at=h.started_at,
            exited_at=time.time() if rc is not None else None,
            pid=h.popen.pid,
        )
        if rc is None:
            return info
        if IS_POSIX and rc < 0:
            info.signal = -rc
        else:
            info.exit_code = rc
        return info

    # ---------- internals ----------
    def _wait_for_exit(self, *, timeout: float) -> None:
        end = time.time() + timeout
        while time.time() < end:
            if not self.is_alive():
                self._win_pid = None
                return
            time.sleep(0.05)

    def _cleanup_files(self) -> None:
        """stdout/stderr のファイルをクローズする（重複クローズ安全）。"""
        h = self.handle
        if not h:
            return
        for fattr in ("_stdout_f", "_stderr_f"):
            f = getattr(h, fattr, None)
            if f:
                try:
                    f.close()
                except Exception:
                    pass
                setattr(h, fattr, None)

# ----------------------
# 単体実行 (__main__)
# ----------------------
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python -m hako_launch.hako_asset_runner <command> <cwd> [args...] [--grace 2.0]")
        sys.exit(1)

    # 簡易パース
    argv = sys.argv[1:]
    grace = 2.0
    if "--grace" in argv:
        i = argv.index("--grace")
        grace = float(argv[i+1])
        argv = argv[:i] + argv[i+2:]
    cmd, *args = argv
    cwd = sys.argv[2]
    runner = AssetRunner()
    h = runner.spawn(cmd, args, cwd=cwd)
    print(f"[runner] spawned PID={h.popen.pid} ({cmd})")

    try:
        while runner.is_alive():
            print("[runner] alive...")
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("[runner] KeyboardInterrupt → terminate")
        runner.terminate(grace_sec=grace)

    info = runner.exit_info()
    print("[runner] exit info:", json.dumps(info.__dict__, indent=2))
