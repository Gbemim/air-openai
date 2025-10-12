



project_name = "tester1"
config_path = "config.yaml"

api_key = str(os.getenv("AIR_API_KEY"))


def main():
    distiller_client = DistillerClient(api_key=api_key)
    distiller_client.create_project(config_path=config_path, project=project_name)


if __name__ == "__main__":
    main()