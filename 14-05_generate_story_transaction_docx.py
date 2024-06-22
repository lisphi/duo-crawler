import os
import pypandoc

def markdown_to_docx(input_filename, output_filename, rewrite):
    if os.path.exists(output_filename):
        if rewrite:
            os.remove(output_filename)
        else:
            print(f"{output_filename} exists")
            return
        
    try:
        output = pypandoc.convert_file(input_filename, 'docx', outputfile=output_filename)
    except Exception as e:
        print(f"An error occurred: {e}")


def main():
    stories_path = './stuff/stories'
    filenames = [name for name in os.listdir(stories_path) if name.endswith('.md')]
    for filename in filenames:
        if '0001-0500' not in filename:
            continue
        input_filename = f"{stories_path}/{filename}"
        output_filename = f"{stories_path}/{filename[:-3]}.docx"
        markdown_to_docx(input_filename, output_filename, False)


if __name__ == '__main__':
    main()