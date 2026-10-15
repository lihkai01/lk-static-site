import os
from block_func import markdown_to_html_node
from extract_title import extract_title

def generate_page(from_path, template_path, dest_path):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    with open(from_path) as f:
        source_text = f.read()

    with open(template_path) as temp_file:
        temp_text = temp_file.read()

    content = markdown_to_html_node(source_text).to_html()
    title = extract_title(source_text)
    new_text = temp_text.replace("{{ Title }}", title)
    new_text = new_text.replace("{{ Content }}", content)

    dir_name = os.path.dirname(dest_path)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    with open(dest_path,mode='w') as dest_file:
        dest_file.write(new_text)

def generate_pages_recursive(dir_path_content, template_path, dest_dir_path):
    for filename in os.listdir(dir_path_content):
        from_path = os.path.join(dir_path_content,filename)
        if os.path.isfile(from_path):
            dest_name = filename.replace(".md",".html")
            dest_path = os.path.join(dest_dir_path,dest_name)
            generate_page(from_path,template_path,dest_path)
        else:
            dest_path = os.path.join(dest_dir_path,filename)
            generate_pages_recursive(from_path, template_path, dest_path)
