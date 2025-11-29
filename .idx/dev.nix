# To learn more about how to use Nix to configure your environment
# see: https://developers.google.com/idx/guides/customize-idx-env
{ pkgs, ... }: {
  # Which nixpkgs channel to use.
  channel = "stable-24.05"; # or "unstable"

  # Use https://search.nixos.org/packages to find packages
  packages = [
    # Create a Python environment with all necessary packages
    (pkgs.python311.withPackages (ps: [
      ps.pip
      ps.flask
      ps.matplotlib
      ps.numpy
      ps.ipykernel
      ps.pytest # Add pytest to the Python environment
      ps.cryptography # Add cryptography
    ]))
  ];

  # Sets environment variables in the workspace
  env = {
    PYTHONPATH = "./caelus";
  };

  idx = {
    # Search for the extensions you want on https://open-vsx.org/ and use "publisher.id"
    extensions = [
      "google.gemini-cli-vscode-ide-companion"
    ];

    # Enable previews
    previews = {
      enable = true;
      previews = {
        web = {
          command = [ "flask" "run" "--port" "$PORT" ];
          manager = "web";
        };
      };
    };

    # Workspace lifecycle hooks
    workspace = {
      # Runs when a workspace is first created
      onCreate = {
        default.openFiles = [ ".idx/dev.nix" "README.md" "app.py" ];
      };
      # Runs when the workspace is (re)started
      onStart = {};
    };
  };
}
