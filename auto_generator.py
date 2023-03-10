from api_notion import Notion
from api_openai import Openai
from api_webflow import Webflow
import json
from pathlib import  Path

# Get config
config_path = Path(r"c:\Users\z0048drc\Documents\Github\BlogAutomation")
if input(f"Is this path correct?\n{config_path} [y/n]: ") == 'n':
    config_path = Path(input("Input a config path: "))
config = json.load(open(config_path/ 'config.json'))

# Get openai api
openai = Openai(config['openai'])

# Get notion api
notion = Notion(config['notion'])
contents = notion.readDatabase('contents')
tags = notion.readDatabase('tags')
categories = notion.readDatabase('categories')

# Get webflow api
webflow_tags = Webflow(config['webflow'], 'tags')
webflow_categories = Webflow(config['webflow'], 'categories')

print("Start blog posts generation!!\n")
for page in contents:
    if not Notion.getDone(page):
        title = Notion.getTitle(page)
        category = Notion.getCategory(page)

        print(f"Blog auto-generation starts for ...\n - Title: {title}\n - Category: {category}")
        print("==============================================")
        # %% Body
        print("Generate the blog body")
        body = openai.run("Body", max_tokens=3800, title=title, category=category)

        # %% Summary
        print("Generate a summary")
        summary = openai.run("Summary", max_tokens=1000, body=body, temperature=0.7)

        # %% Tags
        print("Generate tags")
        tag_names = openai.run("Tags", summary=summary, tags=tags, temperature=0.4)
        tag_ids = Notion.get_tag_id(tags, tag_names)

        # %% Main image
        print("Generate an image")
        image = openai.run("Image", title=title, summary=summary, temperature=0.1)

        # %% Thumbnail image
        print("Generate a thumbnail image")
        thumbnail = openai.run("Thumbnail", title=title, temperature=0.1)

        # %% Get category ID
        category_id = Notion.get_category_id(categories, category)

        notion.updateProperty(page['id'], "Body", 'text', body)
        notion.updateProperty(page['id'], "Summary", 'text', summary)
        notion.updateProperty(page['id'], "Main image", 'files', ("Image", image))
        notion.updateProperty(page['id'], "Thumbnail", 'files', ("Thumbnail", thumbnail))
        notion.updateProperty(page['id'], "Tags_link", 'relation', tag_ids)
        notion.updateProperty(page['id'], "Category_link", 'relation', category_id)
        notion.updateProperty(page['id'], "Done", 'checkbox', True)

        print("Done!\n\n")

print("Generating blog posts is done!")
print("Start to create tags and categories in Webflow")
for page in tags:
    if not Notion.getFeatured(page):
        tag = Notion.getName(page)
        print(f" Uploading Tag: {tag} ... ")
        item_id = webflow_tags.createItem(title=tag)
        notion.updateProperty(page['id'], 'Webflow item ID', 'text', item_id)
        notion.updateProperty(page['id'], "Featured", 'checkbox', True)
        print("  Done!\n")

for page in categories:
    if not Notion.getFeatured(page):
        category = Notion.getName(page)
        print(f" Uploading Tag: {category} ... ")
        item_id = webflow_categories.createItem(title=category)
        notion.updateProperty(page['id'], 'Webflow item ID', 'text', item_id)
        notion.updateProperty(page['id'], "Featured", 'checkbox', True)
        print("  Done!\n")
