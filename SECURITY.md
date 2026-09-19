# Security

Alias Resolver treats its YAML file as trusted application configuration.
Resolving an import or running a lifecycle task imports and executes Python
code, including normal module import side effects.

- Do not accept configuration from an untrusted user or remote request.
- Review dotted import paths as carefully as source code.
- Filesystem aliases are resolved relative to the configuration directory and
  must remain within that directory tree.
- Listing aliases and resolving path aliases do not import configured modules.
- Do not place credentials in the YAML file merely because it is configuration.

Use a minimal synthetic configuration when reporting a defect.
