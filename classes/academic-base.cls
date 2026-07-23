%% ============================================================================
%% academic-base.cls — Clase base del framework (documentos de texto, LuaLaTeX)
%% ----------------------------------------------------------------------------
%% Núcleo sobre `article` que carga la identidad única (styles/academic.sty) y el
%% layout base. NO se usa directamente: de ella heredan academic-exam y
%% academic-report. El diseño vive aquí y en styles/; nunca en los documentos.
%% Motor: LuaLaTeX exclusivamente.
%% ============================================================================
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{academic-base}[2026/07/23 v1 Clase base Academic (LuaLaTeX)]

\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax
\LoadClass[11pt,a4paper]{article}

% --- Identidad visual única ------------------------------------------------
\RequirePackage{academic}

% --- Layout base (los valores tunables viven en config/) -------------------
\RequirePackage{geometry}
\InputIfFileExists{layout.tex}{}{%
  \geometry{a4paper,top=2.6cm,bottom=2.6cm,left=2.4cm,right=2.4cm}}
\setlength{\parindent}{0pt}
\setlength{\parskip}{0.5em plus 2pt minus 1pt}
\linespread{1.06}

% --- Enlaces (color de la identidad) ---------------------------------------
\RequirePackage{hyperref}
\hypersetup{colorlinks=true, allcolors=enlace, breaklinks=true,
  pdfstartview=FitH}

% --- Estructura editorial de títulos ---------------------------------------
\RequirePackage{titlesec}
\titleformat{\section}{\Large\bfseries\color{acento}}{\thesection}{0.6em}{}
\titleformat{\subsection}{\large\bfseries\color{textoprincipal}}{\thesubsection}{0.6em}{}
\titlespacing*{\section}{0pt}{1.2em}{0.5em}

\endinput
