with (import <nixpkgs> {});
mkShell {
  nativeBuildInputs = with pkgs; [
    (python3.withPackages (ps: with ps; [ pydot ]))
    asymptote
    texlive.combined.scheme-medium
  ];
}
