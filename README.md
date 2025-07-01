# hakoniwa-pdu-python

This is a Python PDU communication library for the Hakoniwa simulator.  
It allows easy sending/receiving of PDU binary data and conversion to/from JSON over WebSocket.

---

## 📦 Installation

```bash
pip install hakoniwa-pdu
````

Check the installed version:

```bash
pip show hakoniwa-pdu
```

---

## 🔧 Environment Variables

You can specify the directory containing `.offset` files used for PDU conversion:

```bash
export HAKO_BINARY_PATH=/your/path/to/offset
```

If not set, the default path will be:

```
/usr/local/lib/hakoniwa/hako_binary/offset
```

---

## 🚀 Example Usage

### Read a PDU from drone using test script

The following sample script receives the `pos` PDU from the drone and converts it into JSON.

`tests/sample.py`:

```python
# (your existing sample.py content goes here)
```

### Run example

```bash
python tests/sample.py \
  --config ./config/pdudef/webavatar.json \
  --uri ws://localhost:8765
```

---

## 📁 Package Structure

```
hakoniwa_pdu/
├── pdu_manager.py                  # Manages PDU lifecycle
├── impl/
│   ├── websocket_communication_service.py  # WebSocket implementation
│   ├── pdu_convertor.py            # Binary ⇔ JSON conversion
│   ├── hako_binary/
│   │   └── *.py (Handles offsets and binary layout)
├── resources/
│   └── offset/                     # Offset definition files
```

---

## 🔗 Links

* 📘 GitHub: [https://github.com/hakoniwalab/hakoniwa-pdu-python](https://github.com/hakoniwalab/hakoniwa-pdu-python)
* 🌐 Hakoniwa Lab: [https://hakoniwa-lab.net](https://hakoniwa-lab.net)

---

## 📚 Documentation

For detailed API usage, refer to the full API reference:

➡️ [API Reference (api-doc.md)](./api-doc.md)

---

## 📜 License

MIT License - see [LICENSE](./LICENSE) for details.

```

