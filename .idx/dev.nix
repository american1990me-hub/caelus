
{ pkgs, ... }:
let
  # Define the Caelus package from the local source directory.
  caelus-pkg = pkgs.python311.pkgs.buildPythonPackage {
    pname = "caelus";
    # The version is not critical here as it's a local source build.
    version = "0.1.0-local";
    # The source code is in the `caelus` directory at the project root.
    # The path is relative to this Nix file's location (`.idx/dev.nix`).
    src = ../caelus;

    # Tell Nix to use the pyproject.toml format instead of the default setup.py
    format = "pyproject";

    # Provide the necessary build tools for a pyproject.toml-based build
    # that uses setuptools.
    propagatedBuildInputs = [
      pkgs.python311.pkgs.setuptools
      pkgs.python311.pkgs.wheel
    ];
  };
in
{
  # NixOS channel to use. It's best to pin this for reproducibility.
  channel = "stable-24.05";

  # The list of packages required for your development environment.
  packages = [
    # Python 3.11 with a specific set of libraries.
    (pkgs.python311.withPackages (ps: [
      ps.fastapi      # The web framework for the backend.
      ps.uvicorn      # The web server for FastAPI.
      ps.matplotlib   # For plotting and generating reports.
      ps.numpy        # For numerical operations.
      ps.pytest       # For running tests.
      ps.cryptography # For cryptographic operations.
      ps.scipy        # For scientific computing.
      ps.pandas       # For data analysis.
      ps.z3           # A theorem prover.
      ps.lark         # A parsing library.
      ps.spacy        # For natural language processing.
      ps.tiktoken     # A tokenizer.
      ps.networkx     # For graph analysis.
      caelus-pkg      # Install the local Caelus package.
    ]))
    # Node.js for the frontend UI.
    pkgs.nodejs_20
  ];

  # Environment variables available in your workspace.
  env = {
    # The PYTHONPATH is no longer needed because `caelus` is now a proper
    # installed package.
  };

  # IDX-specific settings.
  idx = {
    # A list of VS Code extensions to install.
    extensions = [
      "google.gemini-cli-vscode-ide-companion" # The Gemini extension.
    ];

    # Web preview settings.
    previews = {
      enable = true;
      previews = {
        # This defines the web preview for the frontend application.
        web = {
          # The command to start the frontend dev server.
          # $PORT is a dynamic port assigned by IDX.
          command = ["npm" "run" "dev" "--" "--port" "$PORT" "--host" "0.0.0.0"];
          # The working directory for the command.
          cwd = "phaseloom-ui";
          # Use the 'web' manager for this preview.
          manager = "web";
        };
      };
    };

    # Workspace lifecycle hooks.
    workspace = {
      # Commands that run only once, when the workspace is first created.
      onCreate = {
        # Install the Node.js dependencies for the frontend UI.
        npm-install = "npm install --prefix phaseloom-ui";
      };
      # Commands that run every time the workspace starts.
      onStart = {
        # Start the backend FastAPI server on port 8000.
        # --reload will automatically restart the server on code changes.
        start-api = "uvicorn phase_loom.main:app --host 0.0.0.0 --port 8000 --reload";
      };
    };
  };
}
