import os
from gitignore_parser import parse_gitignore

def print_structure(startpath, ignore_func, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        for root, dirs, files in os.walk(startpath):
            level = root.replace(startpath, '').count(os.sep)
            indent = ' ' * 4 * level
            f.write(f'{indent}{os.path.basename(root)}/\n')
            subindent = ' ' * 4 * (level + 1)
            for file in files:
                if not ignore_func(os.path.join(root, file)):
                    f.write(f'{subindent}{file}\n')
            dirs[:] = [d for d in dirs if not ignore_func(os.path.join(root, d))]

def main():
    current_dir = os.getcwd()
    project_root = os.path.dirname(current_dir)  # Bir üst dizine çık
    gitignore_file = os.path.join(project_root, '.gitignore')

    if not os.path.exists(gitignore_file):
        print(f"No .gitignore file found at {gitignore_file}")
        return

    ignore_func = parse_gitignore(gitignore_file)
    output_file = os.path.join(current_dir, 'structure.txt')

    print(f"Project root: {project_root}")
    print(f".gitignore file: {gitignore_file}")

    print_structure(project_root, ignore_func, output_file)
    print(f"Project structure has been saved to '{output_file}'.")

    with open(output_file, 'r') as f:
        print("\nProject Structure:")
        print(f.read())

if __name__ == "__main__":
    main()