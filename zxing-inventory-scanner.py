#!/usr/bin/python3

import zxingcpp
import cv2
import argparse
import os


def zxing_decode(filename):
    img = cv2.imread(filename)
    if img is None:
        print('Failed to read image file "{}"'.format(filename))
        return None
    zxing_results = zxingcpp.read_barcodes(img)
    parsed_part = inv_part()
    if parsed_part.parse_from_zxing(zxing_results):
        return parsed_part
    else:
        return None


def part_from_cam_scan():
    cam = cv2.VideoCapture(0)
    captured = False
    zxing_results = None
    parsed_part = None
    while not captured:
        ret, frame = cam.read()
        if not ret:
            print("failed to grab frame")
            break
        cv2.imshow("test", frame)
        zxing_results_act = zxingcpp.read_barcodes(frame)
        update = ((zxing_results is None) or (len(zxing_results) < len(zxing_results_act))) and (
            len(zxing_results_act) >= 1
        )
        if update:
            zxing_results = zxing_results_act
            for result in zxing_results_act:
                print("ZXing Text: {}, format: {}".format(result.text, result.format))
        k = cv2.waitKey(1)
        if k % 256 == 27:
            # ESC pressed
            print("Escape hit, closing...")
            break
        parsed_part = inv_part()
        if parsed_part.parse_from_zxing(zxing_results):
            captured = True
            break
    cam.release()
    cv2.destroyAllWindows()
    if captured:
        return parsed_part
    else:
        return None


class inv_part(object):
    def __init__(self):
        self.value = None
        self.quantity = None
        self.url = None
        self.distributor = None
        self.order_no = None
        self.ordering_no = None

    def parse_from_zxing(self, zxing_results):
        if zxing_results is None:
            return False
        for result in zxing_results:
            flds = result.text.split(chr(9245))
            if len(flds) >= 2:
                for fld in flds:
                    if fld.startswith("1P"):
                        self.value = fld[2:]
                        self.distributor = "Mouser"
                    if fld.startswith("Q"):
                        try:
                            self.quantity = int(fld[1:])
                        except ValueError:
                            print('Quantity parsing failed "{}"'.format(fld[1:]))
            else:
                flds = result.text.split(" ")
                if len(flds) >= 2:
                    for fld in flds:
                        if fld.startswith("PN:"):
                            self.value = fld[3:]
                            self.distributor = "TME"
                        if fld.startswith("QTY:"):
                            try:
                                self.quantity = int(fld[4:])
                            except ValueError:
                                print('Quantity parsing failed "{}"'.format(fld[4:]))

        return (self.value is not None) and (self.quantity is not None)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="ZXing Inventory Scanner")
    parser.add_argument(
        "-o",
        "--output-file",
        dest="inventory_csv",
        type=str,
        default="inventory.csv",
        help="Output CSV file inventory",
    )
    parser.add_argument("qr_files", nargs=argparse.REMAINDER)

    args = parser.parse_args()

    from_files = len(args.qr_files) >= 1
    qr_files_idx = 0
    finish = False

    inventory = {}
    # Load existing CSV if it exists
    if os.path.exists(args.inventory_csv):
        with open(args.inventory_csv, "rt", encoding="utf-8") as fin:
            next(fin)  # skip header
            for line in fin:
                value, quantity, distributor = line.strip().split(",")
                existing_part = inv_part()
                existing_part.value = value
                existing_part.quantity = int(quantity)
                existing_part.distributor = distributor
                inventory[value] = existing_part

    while not finish:
        scan_result = None
        if not from_files:
            scan_result = part_from_cam_scan()
        elif qr_files_idx >= len(args.qr_files):
            finish = True
            break
        else:
            scan_result = zxing_decode(args.qr_files[qr_files_idx])
            qr_files_idx += 1
        if scan_result is not None:
            print(
                "value: {}, quantity: {} distributor: {}".format(
                    scan_result.value, scan_result.quantity, scan_result.distributor
                )
            )
            while True:
                res = input("Specify part {} quantity [{}]:".format(scan_result.value, scan_result.quantity))
                if res == "":
                    break
                try:
                    scan_result.quantity = int(res)
                    break
                except ValueError:
                    print('Quantity parsing failed "{}"'.format(res))
            if scan_result.value in inventory:
                inventory[scan_result.value].quantity += scan_result.quantity
            else:
                inventory[scan_result.value] = scan_result
        else:
            res = input("Do you want to finish [y/n]:")
            if res.lower() == "y":
                finish = True
    with open(args.inventory_csv, "wt", encoding="utf-8") as fout:
        fout.write("value,quantity,distributor\n")
        for value, inventory_part in sorted(inventory.items()):
            fout.write("{},{},{}\n".format(inventory_part.value, inventory_part.quantity, inventory_part.distributor))
