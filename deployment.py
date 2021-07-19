#!/usr/bin/env python3


# pulumi login --local


import os
import sys
import json
import pulumi
from pulumi import automation as auto
from pulumi_kubernetes.apps.v1 import Deployment


def pulumi_program():
    app_labels = { "app": "nginx" }
    deployment = Deployment(
        "nginx",
        spec={
            "selector": { "match_labels": app_labels },
            "replicas": 1,
            "template": {
                "metadata": { "labels": app_labels },
                "spec": { "containers": [{ "name": "nginx", "image": "nginx" }] }
            }
        }
    )
    pulumi.export("name", deployment.metadata["name"])


def main():
    # To destroy our program, we can run python main.py destroy
    destroy = False
    args = sys.argv[1:]
    if len(args) > 0:
        if args[0] == "destroy":
            destroy = True

    project_name = "inline_k8s_project"
    stack_name = "dev"

    # create or select a stack matching the specified name and project.
    # this will set up a workspace with everything necessary to run our inline program (pulumi_program)
    stack = auto.create_or_select_stack(stack_name=stack_name,
                                        project_name=project_name,
                                        program=pulumi_program)

    print("successfully initialized stack")

    # for inline programs, we must manage plugins ourselves
    print("installing plugins...")
    stack.workspace.install_plugin("kubernetes", "v3.5.1")
    print("plugins installed")

    # set stack configuration specifying the AWS region to deploy
    # print("setting up config")
    # stack.set_config("aws:region", auto.ConfigValue(value="us-west-2"))
    # print("config set")

    print("refreshing stack...")
    stack.refresh(on_output=print)
    print("refresh complete")

    if destroy:
        print("destroying stack...")
        stack.destroy(on_output=print)
        print("stack destroy complete")
        sys.exit()

    print("updating stack...")
    up_res = stack.up(on_output=print)
    print(f"update summary: \n{json.dumps(up_res.summary.resource_changes, indent=4)}")


if __name__ == "__main__":
    os.environ["PULUMI_CONFIG_PASSPHRASE"] = ""
    main()
