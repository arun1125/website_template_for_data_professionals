from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
import markdown2
from nbconvert import HTMLExporter
import os
import json

about_data = {}
for _, _, files in os.walk('./about'):
    for file in files:
        with open(f'./about/{file}', 'r') as f:
            text = [line.strip() for line in f.readlines()]
            about_data[file[:-4]] = text

def notebook_to_html(path):
    exporter = HTMLExporter()
    exporter.exclude_input = False  # You can change this depending on whether you want to include the input cells

    with open(path, 'r', encoding='utf-8') as notebook:
        body, _ = exporter.from_file(notebook)
    return body

def read_markdown_file(path):
    with open(path, 'r', encoding='utf-8') as file:
        return markdown2.markdown(file.read())
    
def experience_html(experience_data):
    CompanyName = experience_data['CompanyName']
    Location = experience_data['Location']
    Time = experience_data['Time']
    Title = experience_data['Title']
    Work = experience_data['Work']

    return_html = f"""
        <div class="rounded-lg bg-card text-card-foreground">
            <div class="flex flex-col space-y-1.5">
                <div class="flex items-center justify-between gap-x-2 gap-y-2 text-base">
                    <h3 class="inline-flex flex-wrap items-center gap-x-1 gap-y-2 font-semibold leading-none">
                        <a class="gap-x-2 hover:underline" > {CompanyName} </a>
                            <span class="">
                                <div class="inline-flex items-center rounded-md border px-2 py-0.5 font-semibold font-mono transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 text-nowrap border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/60 align-middle text-xs">
                                    {Location}
                                </div>
                            </span>
                        </h3>
                        <div class="flex-0 text-sm tabular-nums text-gray-500">
                            {Time}
                        </div>
                    </div>
                    <h4 class="font-mono text-sm leading-none">{Title}</h4>
                </div>
        </div>
    """

    for task in Work:
        return_html += f"""
            <div class="text-pretty font-mono text-muted-foreground mt-2 text-xs">
                    <ul> + {Work[task]} </ul>
            </div>
        """

    return return_html

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    experience_htmls = []

    for _, _, files in os.walk('./experience'):
        for file in sorted(files, reverse=True):
            with open(f'./experience/{file}') as f:
                experience_data = json.load(f)
                experience_htmls.append(experience_html(experience_data))

    return templates.TemplateResponse("index.html", {"request": request, "data": about_data, "experience_htmls": experience_htmls})


@app.get("/writing", response_class=HTMLResponse)
async def writings(request: Request):
    folder = './writings'

    categories = []
    for _, subdirList, _ in os.walk(folder):
        for subdir in subdirList:
            categories.append(subdir)

    return templates.TemplateResponse("categories.html", {"request": request, "categories": categories, "category": "writing", "data": about_data})

@app.get("/writing/{category}", response_class=HTMLResponse)
async def load_notebook(request: Request, category: str):
    notebook_folder = f'./writings/{category}'
    notebook_files = [f for f in os.listdir(notebook_folder) if f.endswith('.ipynb')]

    return templates.TemplateResponse("notebooks.html", {"request": request, "category":category, "notebook_files": notebook_files, "data": about_data})


@app.get("/writing/{category}/{notebook_file}", response_class=HTMLResponse)
async def load_notebook(request: Request, category:str, notebook_file: str):
    content = notebook_to_html(f'./writings/{category}/{notebook_file}')
    notebook_folder = f'./writings/{category}'
    notebook_files = [f for f in os.listdir(notebook_folder) if f.endswith('.ipynb')]
    return templates.TemplateResponse("load_notebook.html", {"request": request, "content": content, "notebook_file": notebook_files, "data": about_data})

@app.get("/readinglist", response_class=HTMLResponse)
async def readinglist(request: Request):
    folder = './readings'

    categories = []
    for _, subdirList, _ in os.walk(folder):
        for subdir in subdirList:
            categories.append(subdir)

    return templates.TemplateResponse("categories.html", {"request": request, "categories": categories, "category": "readinglist", "data": about_data})

@app.get("/readinglist/{category}", response_class=HTMLResponse)
async def load_notebook(request: Request, category: str):

    with open(f'./readings/{category}/readinglist.txt', 'r') as f:
        links = [line.strip() for line in f.readlines()]

    return templates.TemplateResponse('readinglist.html', {'request': request, 'links': links, "data": about_data})