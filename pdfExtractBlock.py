import os, sys
import argparse
from pdfquery import PDFQuery
from lxml import etree


def is_directory_or_file(filename, description, allow_file=True):
    if os.path.isdir(filename):
        mode = "DIRECTORY"
        print(f"{description} Directory Provided: {filename}")
    elif os.path.isfile(filename):
        if allow_file:
            print(f"{description} File Provided: {filename}")
            mode = "FILE"
        else:
            print(f"{description} Files not allowed: {filename}")
            mode = "ERROR"
    else:
        print(f"{description}: {filename} is not found")
        mode = "ERROR"
    return mode


def process_commandline():
    parser = argparse.ArgumentParser(
        usage="%(prog)s [-t <target-folder>] -s SectionStartMarker -e SectionEndMarker <filename-or-folder>"
    )
    parser.add_argument(
        "-t", "--target", default='$COPY_SRC'
    )
    parser.add_argument(
        "-s", "--section"
    )
    parser.add_argument(
        "-e", "--endMarker"
    )
    parser.add_argument("filename")  # positional parameter so mandatory
    args = parser.parse_args()

    filename_mode = is_directory_or_file(args.filename, "-f <Filename-Or-Folder>")
    if args.target == '$COPY_SRC' and filename_mode == "DIRECTORY":
        args.target = args.filename
    target_mode = is_directory_or_file(args.target, "-t <Target>")

    return filename_mode, target_mode, args


def save_list_to_file(filename, data_list=None, data = None):
    with open(filename, mode='wt', encoding='utf-8') as myfile:
        if data_list is not None:
            myfile.write('\n'.join(data_list))
        elif data is not None:
            myfile.write(data)


def get_section_of_list(items, section_marker="", end_marker=""):
    if section_marker != "":
        start_index, start_item = next(iter((i, t) for i,t in enumerate(items)
                                            if section_marker.lower() in t.lower() ), None)
    else:
        start_index = None

    if end_marker != "":
        end_index, end_item = next(iter((i, t) for i,t in enumerate(items)
                                        if i > start_index and end_marker in t), None)
    else:
        end_index = None

    if start_index is not None and end_index is not None:
        items = [t.strip() for i,t in enumerate(items) if i >= start_index if i < end_index]
    elif start_index is not None:
        items = [t for i, t in enumerate(items) if i >= start_index]
    elif end_index is not None:
        items = [t for i, t in enumerate(items) if i < end_index]

    return items


def format_lines(lines):
    """
    remove blanks lines before list items.
    remove blank lines if previous line doesn't end in .
    :param lines:
    :return:
    """
    out_lines = []
    out_line_number = 0
    for i,line in enumerate(lines):
        out_lines.append(line)

        if line == '' and i > 1 and out_lines[out_line_number - 1].endswith('.') is False:
            out_lines.pop(out_line_number)  # remove this blank line
            out_line_number -= 1

        if line.startswith('-') and i > 0: # remove blank lines between list items
            if out_lines[out_line_number-1] == '':
                out_lines.pop(out_line_number-1)
                out_line_number -= 1
        out_line_number += 1

    return out_lines


def read_file_to_list(filename, section_marker="", end_marker=""):
    with open(filename, mode='r', encoding='utf-8') as myfile:
        lines = myfile.readlines()

    return lines


def pdf_extract_block(filename, target_folder, section_marker, end_marker=""):
    # build the target_filename
    filename_only = os.path.basename(filename)
    filename_root = os.path.splitext(filename_only)
    target_file = target_folder + '/' + filename_root[0] + ".txt"
    xml_target_file = target_folder + '/' + filename_root[0] + ".xml"
    print(f"pdf_extract_block {filename} {target_file} Section Marker from {section_marker} to {end_marker}")

    pdf = PDFQuery(filename)
    pdf.load()

    pdf.tree.write(xml_target_file, pretty_print=True)
    lines = read_file_to_list(xml_target_file)
    save_list_to_file(xml_target_file, lines)

    tree = etree.parse(xml_target_file)
    no_tags = etree.tostring(tree, encoding='utf8', method='text').decode("utf-8") # convert bytes to string
    print(no_tags)

    lines = get_section_of_list(no_tags.split('\n'), section_marker, end_marker)
    # save_list_to_file(target_file + '2', data_list=lines)
    lines = format_lines(lines)
    save_list_to_file(target_file, data_list=lines )



def pdfQueryMethod(pdf, section_marker, end_marker):
    """
    Doest work
    :return:
    """
    text_elements = pdf.pq("LTTextBoxHorizontal")
    start_index, start_item = next(iter((i, t.text) for i,t in enumerate(text_elements) if t.text.lower().startswith(section_marker.lower())), None)
    print(f"Item={start_item} -> {start_index}")
    end_index, end_item = next(iter((i, t.text) for i,t in enumerate(text_elements) if i > start_index and t.text.startswith(end_marker)), None)
    print(f"Item={end_item} -> {end_index}")

    if start_index is not None and end_index is not None:
        text = [t.text for i,t in enumerate(text_elements) if i > start_index if i < end_index]
    elif end_index is None:
        text = [t.text for i, t in enumerate(text_elements) if i > start_index]
    elif start_index is None:
        text = [t.text for i, t in enumerate(text_elements) if i < end_index]
    else:
        text = [t.text for i, t in enumerate(text_elements) if i < end_index]

    print(text)



def pdf_extract_block_command():
    filemode, target_mode, args = process_commandline()
    print(f"{filemode} {target_mode} {args}")
    if filemode == "ERROR" or target_mode=="ERROR":
        return

    if filemode == "DIRECTORY":
        for file in os.listdir(args.filename):
            name = os.fsdecode(file)
            if name.endswith(".pdf"):
                fullname = os.path.join(args.filename, name)
                print(fullname)
                pdf_extract_block(fullname, args.target, args.section, args.endMarker)
            else:
                continue
    elif filemode == "FILE":
        pdf_extract_block(args.filename, args.target, args.section, args.endMarker)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    pdf_extract_block_command()


