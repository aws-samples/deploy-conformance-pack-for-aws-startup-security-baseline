import jinja2
from aws_cdk import Aws


def render_template(data):
    template_loader = jinja2.FileSystemLoader(searchpath="./conformance_pack/templates/")
    template_env = jinja2.Environment(loader=template_loader, autoescape=True)
    TEMPLATE_FILE = "conformance_pack.jinja"
    template = template_env.get_template(TEMPLATE_FILE)
    return template.render(data=data)


def localise_rules_stack(data):
    for rule in data['conformance_pack']['rules']:
        for key, value in rule.items():
            if key in ("resourceID", "awsPrincipals"):
                rule[key] = value.replace("${AWS::AccountId}", str(Aws.ACCOUNT_ID))
    return data


def filter_ignore_list(rules: list, ignore_list: list):
    for rule in rules:
        if rule['resource_name'] in ignore_list:
            rules.remove(rule)
    return rules
