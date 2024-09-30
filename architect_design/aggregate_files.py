import os
from save_structure import main as structere_save

def parse_structure(structure_file):
    with open(structure_file, 'r') as f:
        lines = f.readlines()

    files = []
    current_path = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        
        indent = len(line) - len(line.lstrip())
        level = indent // 4

        if level < len(current_path):
            current_path = current_path[:level]

        if stripped.endswith('/'):
            current_path.append(stripped[:-1])
        else:
            full_path = '/'.join(current_path + [stripped])
            files.append(full_path)

    return files, lines
 
def aggregate_file_contents(file_paths, root_dir, output_file, structure_content):
    with open(output_file, 'w', encoding='utf-8') as out_f:
        # First, write the structure
        
        out_f.write("Project Structure:\n\n")
        out_f.write(''.join(structure_content))
        out_f.write("\n" + "="*50 + "\n\n")
        
        # Then, write file contents
        out_f.write("File Contents:\n\n")
        for file_path in file_paths:
            if file_path.startswith('multivendor-catalog/'):
                file_path = file_path[len('multivendor-catalog/'):]
            
            full_path = os.path.join(root_dir, file_path)
            out_f.write(f"{file_path} :\n\n")
            if os.path.exists(full_path):
                try:
                    with open(full_path, 'r', encoding='utf-8') as in_f:
                        content = in_f.read()
                        out_f.write(content)
                except UnicodeDecodeError:
                    out_f.write("Binary file, content not displayed.\n")
                except Exception as e:
                    out_f.write(f"Error reading file: {str(e)}\n")
            else:
                out_f.write(f"File not found. (Searched at: {full_path})\n")
            out_f.write("\n\n" + "="*50 + "\n\n")

def main():
    structere_save()

    current_dir = os.getcwd()
    project_root = os.path.dirname(current_dir)  # Bir üst dizine çık
    structure_file = os.path.join(current_dir, 'structure.txt')
    output_file = os.path.join(current_dir, 'all_files_content.txt')

    if not os.path.exists(structure_file):
        print(f"structure.txt file not found at {structure_file}")
        return

    print(f"Project root: {project_root}")
    print(f"Structure file: {structure_file}")
    print(f"Output file: {output_file}")

    file_paths, structure_content = parse_structure(structure_file)
    aggregate_file_contents(file_paths, project_root, output_file, structure_content)
    print(f"Project structure and file contents have been aggregated in '{output_file}'.")

if __name__ == "__main__":
    main()