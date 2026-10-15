import re
from enum import Enum
from htmlnode import ParentNode
from textnode import TextNode, TextType, text_to_textnodes, text_node_to_html_node

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"

def block_to_block_type(markdown_text: str) -> BlockType:
    lines = markdown_text.split("\n")

    # Check for Heading
    if lines[0].startswith(("# ","## ","### ","#### ","##### ","###### ")):
        return BlockType.HEADING

    # Check for Code
    if len(lines) >= 2:
        if lines[0].startswith("```") and lines[-1].startswith("```"):
            return BlockType.CODE

    # Check for Quote
    if lines[0].startswith(">"):
        for line in lines:
            if not line.startswith(">"):
                return BlockType.PARAGRAPH
        return BlockType.QUOTE

    # Check for Ordered List
    if lines[0].startswith("- "):
        for line in lines:
            if not line.startswith("- "):
                return BlockType.PARAGRAPH
        return BlockType.UNORDERED_LIST

    # Check for Unordered List
    if lines[0].startswith("1. "):
        i = 1
        for line in lines:
            if not line.startswith(f"{i}. "):
                return BlockType.PARAGRAPH
            i += 1
        return BlockType.ORDERED_LIST

    return BlockType.PARAGRAPH
    
def markdown_to_blocks(markdown_text: str) -> list[str]:
    block = []
    contents = markdown_text.split("\n\n")
    for text in contents:
        if text == "":
            continue
        block.append(text.strip().replace("\t",""))

    return block

def block_type_to_html_type(block_type, markdown_text=None):
    if block_type == BlockType.PARAGRAPH:
        return "p"
    elif block_type == BlockType.CODE:
        return "pre"
    elif block_type == BlockType.QUOTE:
        return "blockquote"
    elif block_type == BlockType.UNORDERED_LIST:
        return "ul"
    elif block_type == BlockType.ORDERED_LIST:
        return "ol"
    elif block_type == BlockType.HEADING:
        match = re.match(r'#+',markdown_text)
        return f"h{len(match.group())}"

def text_to_children(text):
    # step 1: turn `text` into a list of TextNode objects
    text_nodes = text_to_textnodes(text)
    html_nodes = []
    # step 2: for each TextNode, convert it to an HTMLNode
    for node in text_nodes:
        html_nodes.append(text_node_to_html_node(node))
    # step 3: return the list of HTMLNodes
    return html_nodes

def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    html_nodes = [] # collects one html_node per block
    for block in blocks:
        type = block_to_block_type(block)

        if type == BlockType.PARAGRAPH:
            # clean up text somehow
            text = block.replace("\n"," ")
            # then call text_to_children
            text = text_to_children(text)
            # then build the html_node
            html_node = ParentNode(block_type_to_html_type(type), children=text)
        
        elif type == BlockType.HEADING:
            # strip the #'s and space
            text = re.sub(r'#+ ',"",block)
            text = text_to_children(text)
            html_node = ParentNode(block_type_to_html_type(type,block), children=text)

        elif type == BlockType.CODE:
            # strip backticks
            text = block.replace("```\n","")
            text = text.replace("```","")
            # make ONE TextNode manually, skip text_to_children
            text_node = TextNode(text,TextType.CODE)
            # wrap in code node, wrap that in pre node
            node = text_node_to_html_node(text_node)
            html_node = ParentNode("pre",children=[node])

        elif type == BlockType.QUOTE:
            text = block.replace("> ","")
            text = text.replace("\n"," ")
            text = text_to_children(text)
            html_node = ParentNode(block_type_to_html_type(type), children=text)

        elif type == BlockType.UNORDERED_LIST:
            texts = block.split("\n")
            text_nodes = []
            for line in texts:
                text = line.replace("- ","")
                text = text_to_children(text)
                text_nodes.append(ParentNode("li",children=text))
            html_node = ParentNode(block_type_to_html_type(type), children=text_nodes)

        elif type == BlockType.ORDERED_LIST:
            texts = block.split("\n")
            text_nodes = []
            counter = 1
            for line in texts:
                text = line.replace(f"{counter}. ","")
                text = text_to_children(text)
                text_nodes.append(ParentNode("li",children=text))
                counter += 1
            html_node = ParentNode(block_type_to_html_type(type), children=text_nodes)   

        html_nodes.append(html_node)
    
    return ParentNode("div",children=html_nodes)