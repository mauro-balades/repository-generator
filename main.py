import requests
import sys
import os

DEFAULT_NAME = 'REPOS.md'
NAME_SELECTOR = "{{name}}"
LIST_SELECTOR = "{{list}}"
REPOS_SELECTOR = "{{repos}}"

def log(text: str, warn: bool = False):
  if warn:
    print(f"WARNING: {text}")
    return

  print(f"LOG: {text}")

def throwError(error: str):
  raise Exception(error)

def fetchRepos(userName: str):
  response = requests.get(f'https://api.github.com/users/{userName}/repos')

  if response.status_code == 200:
    return response.json()
  else:
    throwError(response.json()['message'])

def getLanguages(repos: list):

  languages = []

  for repo in repos:
    lang = repo['language'] or 'unknown'

    if lang not in languages:
      languages.append(lang)
    
  return languages

def getArgs():
  argv = sys.argv
  result = {}

  if len(argv) > 1:
    result['github_name'] = argv[1]
  else:
    throwError("GitHub name not provided")

  if len(argv) > 2:
    result['output'] = argv[2]
  else:
    log('Output not specified, default output will be ' + DEFAULT_NAME, True)
    result['output'] = DEFAULT_NAME

  return result  

def getTemplatesPath():
  return os.path.join('template', 'template.md')

def getTemplate():
  path = getTemplatesPath()
  content = ""

  with open(path, "r") as f:
    content = f.read()
    f.close()

  return content

def prepareTemplate(args: dict, repos: list, langs: list, template: str):
  
  content_list = ""
  sections = ""
  used_langs = []
  used_repos = []

  for lang in langs:
    _list = f'\n* [{lang}](#{lang})'
    content_list += _list


    for repo in repos:

      repo['language'] = repo['language'] or 'unknown'

      if lang in used_langs:
        title = ''
      else:
        title = f'\n\n## {lang}'
        used_langs.append(lang)

      if (repo['language'] == lang) and (repo['full_name'] not in used_repos):
        desc = ''
        used_repos.append(repo['full_name'])

        desc += f'\n[{repo["full_name"]}]({repo["html_url"]})'

        if repo["description"]:
          desc += f'\n\n{repo["description"]}'
        
        desc += f'\n\nclone: `$ git clone {repo["clone_url"]}`'
        desc += '\n\n\n'
        
        if repo["homepage"]:
          desc += f'\[[homepage]({repo["homepage"]})\] '
        if repo['license']:
          desc += f'[license: {repo["license"]["name"]}]'
      else:
        desc = ''

      sections += title + desc + '\n'
    

  template = template.replace(NAME_SELECTOR, args['github_name'])
  template = template.replace(LIST_SELECTOR, content_list)
  template = template.replace(REPOS_SELECTOR, sections)

  return template

def createOutput(args: dict, content: str):
  with open(args['output'], "w") as f:
    f.write(content)
    f.close()

def main():
  arguments = getArgs()
  repos = fetchRepos(arguments['github_name'])
  languages = getLanguages(repos)
  template = prepareTemplate(arguments, repos, languages, getTemplate())
  createOutput(arguments, template)

if __name__ == "__main__":
  main()