from enum import Enum
from htmlnode import LeafNode
import re


class TextType(Enum):
    TEXT = "text"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"

class TextNode:
    def __init__(self,  text, text_type, url: str | None = None):
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TextNode):
            return False
        return (
            self.text_type == other.text_type
            and self.text == other.text
            and self.url == other.url
        )

    def __repr__(self) -> str:
        return f"TextNode({self.text}, {self.text_type.value}, {self.url})"

def text_node_to_html_node(text_node: TextNode) -> LeafNode:
    if text_node.text_type not in TextType:
        raise Exception("Not a valid text type!")
    elif text_node.text_type == TextType.TEXT:
        node = LeafNode(None, text_node.text)
        return node
    elif text_node.text_type == TextType.BOLD:
        node = LeafNode("b", text_node.text)
        return node
    elif text_node.text_type == TextType.ITALIC:
        node = LeafNode("i", text_node.text)
        return node
    elif text_node.text_type == TextType.CODE:
        node = LeafNode("code", text_node.text)
        return node
    elif text_node.text_type == TextType.LINK:
        node = LeafNode("a", text_node.text, {"href": text_node.url})
        return node
    elif text_node.text_type == TextType.IMAGE:
        node = LeafNode("img", text_node.text)
        return node

def split_nodes_delimiter(old_nodes: list[TextNode], delimiter: str, text_type: TextType) -> list[TextNode]:
    new_nodes = []
    for node in old_nodes:
        if node.text_type is not TextType.TEXT:
            new_nodes.append(node)
        else:
            texts = node.text.split(delimiter)
            if len(texts) % 2 == 0:
                raise Exception("Unbalanced delimeters!")
            for i,text in enumerate(texts):
                if text == "":
                    continue
                if i % 2 == 0:
                    new_node = TextNode(text,TextType.TEXT)
                else:
                    new_node = TextNode(text,text_type)
                new_nodes.append(new_node)
    return new_nodes

def extract_markdown_images(text):
    matches = re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return matches

def extract_markdown_links(text):
    matches = re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return matches

def split_nodes_image(old_nodes: list[TextNode]) -> list[TextNode]:
    new_nodes = []
    for node in old_nodes:
        image_links = extract_markdown_images(node.text)
        if len(image_links) == 0:
            new_nodes.append(node)
        else:
            ori_text = node.text
            for image_alt, image_link in image_links:
                if ori_text == "":
                    continue
                sections = ori_text.split(f"![{image_alt}]({image_link})", 1)
                text_node = TextNode(sections[0],TextType.TEXT)
                new_nodes.append(text_node)
                img_node = TextNode(image_alt, TextType.IMAGE, image_link)
                new_nodes.append(img_node)
                ori_text = sections[1]
                #print(image_alt, image_link, sections)
    return new_nodes

def split_nodes_link(old_nodes: list[TextNode]) -> list[TextNode]:
    new_nodes = []
    for node in old_nodes:
        links = extract_markdown_links(node.text)
        if len(links) == 0:
            new_nodes.append(node)
        else:
            ori_text = node.text
            for link_alt, link in links:
                if ori_text == "":
                    continue
                sections = ori_text.split(f"[{link_alt}]({link})", 1)
                text_node = TextNode(sections[0],TextType.TEXT)
                new_nodes.append(text_node)
                link_node = TextNode(link_alt, TextType.LINK, link)
                new_nodes.append(link_node)
                ori_text = sections[1]
                
    return new_nodes

def text_to_textnodes(text: str) -> list[TextNode]:
    nodes = [TextNode(text,TextType.TEXT)]
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return nodes
    
