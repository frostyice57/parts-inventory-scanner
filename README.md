# parts-inventory-scanner

Scan QR labels from electronic component distributors and build a CSV parts inventory.

The script currently understands QR formats used by:
- Mouser
- TME

It can scan from:
- a webcam feed
- image files passed on the command line

## Requirements

- Python 3
- A webcam for live scanning
- Python packages:
	- `zxing-cpp`
	- `opencv-python`
	- `numpy`

## Install

Install the Python dependencies with:

```bash
pip install zxing-cpp opencv-python numpy
```

Important detail: the ZXing-C++ Python binding is installed as `zxing-cpp`, but imported in code as `zxingcpp`.

The barcode decoding backend comes from the ZXing-C++ project:

https://github.com/zxing-cpp/zxing-cpp

If your platform or Python version does not have a prebuilt wheel, you may need to build the binding from source. In that case, follow the upstream Python wrapper and build instructions in the ZXing-C++ repository.

## Usage

### Webcam mode

Run without positional arguments to scan from the default camera:

```bash
python zxing-inventory-scanner.py
```

Controls:
- `ESC`: quit scanning

When a part is detected, it is captured automatically. The script then prints the decoded value and quantity and lets you override the quantity before writing it to the inventory.

### Image-file mode

Pass one or more image files:

```bash
python zxing-inventory-scanner.py label1.png label2.jpg
```

### Custom output file

By default, the script writes to `inventory.csv`. Use `-o` or `--output-file` to choose a different file:

```bash
python zxing-inventory-scanner.py -o parts.csv
python zxing-inventory-scanner.py -o parts.csv label1.png label2.jpg
```

## Output

The inventory file is written as CSV with this header:

```csv
value,quantity,distributor
```

If the output file already exists, the script loads it first and adds newly scanned quantities to existing rows with the same part value.

## Notes

- Distributor-specific parsing is currently limited to Mouser and TME QR label formats.
- Image-file scanning is supported. If no supported Mouser/TME QR payload is found, the scan is treated as no result.
