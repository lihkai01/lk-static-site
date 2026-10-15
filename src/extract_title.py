def extract_title(markdown:str) -> str:
    lines = markdown.split("\n")

    for line in lines:
        if line.startswith("# "):
            return line.replace("# ","",1).strip()

    raise Exception("No h1 header.")

    
    