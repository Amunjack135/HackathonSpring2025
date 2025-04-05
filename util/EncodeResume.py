import base64
import zlib
import tkinter.filedialog as fd


def main():
    input_file: str = fd.askopenfilename(defaultextension='txt', filetypes=(('Text File', '.txt'),))

    if input_file is None:
        return

    try:
        with open(input_file, 'r') as f:
            contents: str = f.read()
            print(f'Encoded Resume Contens:\n\n{base64.b64encode(zlib.compress(contents.encode(), zlib.Z_BEST_COMPRESSION))}')
    except FileNotFoundError:
        print('Specified file does not exist')


if __name__ == '__main__':
    main()
