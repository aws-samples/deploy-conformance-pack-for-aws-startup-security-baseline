import jinja2

def render_template(data):
    templateLoader = jinja2.FileSystemLoader(searchpath="./conformance_pack/templates/")
    templateEnv = jinja2.Environment(loader=templateLoader, autoescape=True)
    TEMPLATE_FILE = "conformance_pack.jinja"
    template = templateEnv.get_template(TEMPLATE_FILE)
    return template.render(data=data)

def filter_ignore_list(rules: list, ignore_list: list):
    for rule in rules:
        if rule['resource_name'] in ignore_list:
            rules.remove(rule)
    return rules
