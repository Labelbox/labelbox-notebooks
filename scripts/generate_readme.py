import pandas
import glob
from collections import defaultdict
from typing import Dict
import copy

"""
Script used to generate readme programmatically works by taking the links of all the notebooks
then dividing them to different tables based on directory name. Pandas is used to make the tables. Using inline HTML to support our doc page. 
"""

IGNORE = ["template.ipynb"]

ORDER = [
    "basics",
    "exports",
    "project_configuration",
    "annotation_import",
    "integrations",
    "model_experiments",
    "prediction_upload",
]

# Below lists represent a special order for certain sections
BASICS_ORDER = [
    "basics/quick_start.ipynb",
    "basics/basics.ipynb",
    "basics/data_rows.ipynb",
    "basics/data_row_metadata.ipynb",
    "basics/batches.ipynb",
    "basics/projects.ipynb",
    "basics/ontologies.ipynb",
    "basics/user_management.ipynb",
]

SDK_EXAMPLE_HEADER = """
# Labelbox SDK Examples\n
Welcome to Labelbox Notebooks! These documents are directly linked from our Labelbox Readme [Python tutorials](https://docs.labelbox.com/page/tutorials) page and we've set up this GitHub repository for content management. Once a PR is merged to main, the modified notebook is changed in Google colab which are linked throughout our documentation. For more information on the format of our notebooks visit our [CONTRIBUTING.md](./CONTRIBUTING.md).
"""

README_EXAMPLE_HEADER = """---
title: Python tutorials
---

"""

COLAB_TEMPLATE = "https://colab.research.google.com/github/Labelbox/labelbox-notebooks/blob/main/{filename}"
GITHUB_TEMPLATE = "https://github.com/Labelbox/labelbox-notebooks/tree/main/{filename}"

def special_order(link_dict: Dict[str, list]) -> Dict:
    """This is used to add a special order to certain sections. It makes a copy of the link dict provided then loops through items inside the link dict to create a specified order. (Not random) anything not found in the global variable for the section is just tacked on to the end.
    """
    modified_link_dict = copy.deepcopy(link_dict)
    for section, links in link_dict.items():
        
        if section == "basics":
            basic_order = BASICS_ORDER
            for link_name in links:
                if link_name not in BASICS_ORDER:
                    basic_order.append(link_name)
            modified_link_dict[section] = basic_order
    
    return modified_link_dict


def create_header(link: str) -> str:
    """Creates headers of tables with h2 tags to support readme docs

    Args:
        link (str): file path

    Returns:
        str: formatted file path for header
    """
    # Splits up link uses directory name
    split_link = link.split("/")[0].replace("_", " ").split(" ")
    header = []

    # Capitalize first letter of each word
    for word in split_link:
        header.append(word)
    return f"<h2>{' '.join(header).capitalize()}</h2>"


def create_title(link: str) -> str:
    """Create notebook titles will be name of notebooks with _ replaced with spaces and file extension removed

    Args:
        link (str): file path

    Returns:
        str: formatted file path for notebook title
    """
    split_link = link.split(".")[-2].split("/")[-1].replace("_", " ").split(" ")
    title: list[str] = []

    # List for lower casing certain words, keep certain acronyms capitalized and special mappings
    lower_case_words = ["to"]
    acronyms = ["html", "pdf", "llm", "dicom", "sam", "csv"]
    special = {"yolov8": "YOLOv8"}
    first_word = True
    for word in split_link:
        if word.lower() in acronyms:
            title.append(word.upper())
        elif word.lower() in lower_case_words:
            title.append(word.lower())
        elif word in special.keys():
            title.append(special[word])
        else:
            if first_word:
                title.append(word.capitalize())
            else:
                title.append(word)
        first_word = False
    title = " ".join(title).split(".")[0]
    return title


def make_link(link: str, photo: str, link_type: str) -> str:
    """Creates the links for the notebooks as an anchor tag

    Args:
        link (str): file path
        photo (str): photo link
        link_type (str): type of link (github, google colab)

    Returns:
        str: anchor tag with image
    """
    return f'<a href="{link}" target="_blank"><img src="{photo}" alt="Open In {link_type}"></a>'


def make_links_dict(links: str):
    """Creates dictionary needed for pandas to generate the table takes all the links and makes each directory its own table

    Args:
        links (list[str]): list of links to notebooks from glob

    Returns:
        defaultdict[list]: returns dict that is in pandas dataFrame format
    """
    link_dict = defaultdict(list)
    for section in ORDER:
        link_dict[section] = []
    for link in links:
        if link.split("/")[-1] in IGNORE:
            continue
        else:
            split_link = link.split("/")[0]
            link_dict[split_link].append(link)
    return link_dict


def make_table(base: str) -> str:
    """main function to make table

    Args:
        base (str): Header of file generated. Defaults to an empty string.

    Returns:
        str: markdown string file
    """
    link_dict = make_links_dict(glob.glob("**/*.ipynb", recursive=True))
    link_dict = special_order(link_dict)
    generated_markdown = base
    for link_list in link_dict.values():
        pandas_dict = {"Notebook": [], "Google colab": [], "Github": []}
        generated_markdown += f"{create_header(link_list[0])}\n\n"
        for link in link_list:
            pandas_dict["Notebook"].append(create_title(link))
            pandas_dict["Google colab"].append(
                make_link(
                    COLAB_TEMPLATE.format(filename="/".join(link.split("/"))),
                    "https://colab.research.google.com/assets/colab-badge.svg",
                    "Colab",
                )
            )
            pandas_dict["Github"].append(
                make_link(
                    GITHUB_TEMPLATE.format(filename="/".join(link.split("/"))),
                    "https://img.shields.io/badge/GitHub-100000?logo=github&logoColor=white",
                    "Github",
                )
            )
        df = pandas.DataFrame(pandas_dict)
        generated_markdown += f"{df.to_html(col_space={'Notebook':400}, index=False, escape=False, justify='left')}\n\n"
    return f"{generated_markdown.rstrip()}\n"


def main(github: bool):
    """
    Args:
        github (bool): if this is the readme for github.
    """
    if github:
        with open("./README.md", "w") as readme:
            readme.write(make_table(SDK_EXAMPLE_HEADER))
    else:
        with open("./tutorials.html", "w") as readme:
            readme.write(make_table(README_EXAMPLE_HEADER))


if __name__ == "__main__":
    main(True)
