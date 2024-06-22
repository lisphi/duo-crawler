import json
import os

def merge_md(source_filenames, target_filename, rewrite):
    if os.path.exists(target_filename):
        if rewrite:
            os.remove(target_filename)
        else:
            print(f"{target_filename} exists")
            return
    with open(target_filename, 'w', encoding='utf-8') as outfile:
        for filename in source_filenames:
            if os.path.isfile(filename):
                with open(filename, 'r', encoding='utf-8') as infile:
                    content = infile.read()
                    outfile.write(content)
                    outfile.write('\n')  # Add a newline after each file's content
            else:
                print(f"File {filename} does not exist.")

def merge(size, rewrite):
    stories_path = './stuff/stories'
    storie_dir_names = [name for name in os.listdir(stories_path) if os.path.isdir(f"{stories_path}/{name}")]
    source_md_filenames = []
    for i in range(len(storie_dir_names)):
        storie_dir_name = storie_dir_names[i]
        filename = f"{storie_dir_name[:4]}_{storie_dir_name[11:].split('_')[0]}.md"
        md_filename = os.path.join(stories_path, storie_dir_name, filename)
        source_md_filenames.append(md_filename)
        if (i+1)%size == 0 or i == len(storie_dir_names) - 1:
            target_md_filename = os.path.join(stories_path, f"{i//size*size+1:04d}-{(i//size+1)*size:04d}.md")
            merge_md(source_md_filenames, target_md_filename, rewrite)
            source_md_filenames = []
        print(f"progress: {(i + 1.0) / len(storie_dir_names):.2%}")

def main():
    merge(500, False)
        

if __name__ == '__main__':
    main()    