%% ============================================================================
%% academic-report.cls — Documentos de gestión docente (LuaLaTeX)
%% ----------------------------------------------------------------------------
%% Sílabos, calendarios, notas de docente (guiones de clase), manuales, guías,
%% rúbricas. Hereda academic-base (identidad única) y añade metadatos +
%% encabezado institucional + cabeceras/pie. El diseño vive en la base y styles/.
%% Motor: LuaLaTeX exclusivamente.
%% ============================================================================
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{academic-report}[2026/07/23 v1 Gestion docente Academic (LuaLaTeX)]

\DeclareOption*{\PassOptionsToClass{\CurrentOption}{academic-base}}
\ProcessOptions\relax
\LoadClass{academic-base}
\RequirePackage{fancyhdr}
\RequirePackage{enumitem}

% --------------------------------------------------------------- metadatos ---
\def\ar@universidad{}\newcommand{\universidad}[1]{\def\ar@universidad{#1}}
\def\ar@facultad{}\newcommand{\facultad}[1]{\def\ar@facultad{#1}}
\def\ar@escuela{}\newcommand{\escuela}[1]{\def\ar@escuela{#1}}
\def\ar@curso{}\newcommand{\curso}[1]{\def\ar@curso{#1}}
\def\ar@codigocurso{}\newcommand{\codigocurso}[1]{\def\ar@codigocurso{#1}}
\def\ar@docente{}\newcommand{\docente}[1]{\def\ar@docente{#1}}
\def\ar@periodo{}\newcommand{\periodo}[1]{\def\ar@periodo{#1}}
\def\ar@tipodocumento{Documento}\newcommand{\tipodocumento}[1]{\def\ar@tipodocumento{#1}}
\def\ar@titulo{}\newcommand{\titulodocumento}[1]{\def\ar@titulo{#1}}
\def\ar@subtitulo{}\newcommand{\subtitulo}[1]{\def\ar@subtitulo{#1}}
\def\ar@logo{}\newcommand{\logoinstitucional}[1]{\def\ar@logo{#1}}

% ---------------------------------------------------------- cabecera / pie ---
\pagestyle{fancy}\fancyhf{}
\fancyhead[L]{{\small\scshape\color{secundario}\ar@curso}}
\fancyhead[R]{{\small\scshape\color{secundario}\ar@tipodocumento}}
\fancyfoot[C]{{\footnotesize\color{secundario}\thepage}}
\renewcommand{\headrule}{{\color{filete}\hrule width\headwidth height 0.4pt}}
\renewcommand{\headrulewidth}{0.4pt}

% ------------------------------------------------- encabezado institucional --
% \encabezado — bloque de cabecera (institución + tipo + título + curso/docente).
\newcommand{\encabezado}{%
  \thispagestyle{plain}%
  \begin{minipage}[c]{0.74\textwidth}
    {\large\scshape\bfseries\color{acento}\ar@universidad\par}
    \ifdefempty{\ar@facultad}{}{{\small\scshape\color{secundario}\ar@facultad\par}}
    \ifdefempty{\ar@escuela}{}{{\small\scshape\color{secundario}\ar@escuela\par}}
  \end{minipage}\hfill
  \begin{minipage}[c]{0.24\textwidth}\raggedleft
    \ifdefempty{\ar@logo}{}{\includegraphics[height=1.7cm]{\ar@logo}}%
  \end{minipage}\par\vspace{0.6em}
  {\color{acento}\hrule height 0.6pt}\vspace{0.7em}
  \begin{center}
    {\Large\bfseries\scshape\color{acento}\ar@tipodocumento\par}
    \ifdefempty{\ar@titulo}{}{\vspace{0.15em}{\large\color{textoprincipal}\ar@titulo\par}}
    \vspace{0.25em}{\normalsize\itshape\color{secundario}\ar@curso
      \ifdefempty{\ar@codigocurso}{}{ (\ar@codigocurso)}\par}
    \ifdefempty{\ar@subtitulo}{}{{\small\color{secundario}\ar@subtitulo\par}}
  \end{center}\vspace{0.4em}
  {\small\color{secundario}%
   \ifdefempty{\ar@docente}{}{\textbf{Docente:}\ \ar@docente\hfill}%
   \ifdefempty{\ar@periodo}{}{\textbf{Periodo:}\ \ar@periodo}\par}%
  \vspace{0.3em}{\color{filete}\hrule height 0.4pt}\vspace{1em}}

% ---------------------------------------------------- utilidades de gestión --
% \datofila{Etiqueta}{valor} — fila de datos generales (sílabo, etc.)
\newcommand{\datofila}[2]{\noindent\makebox[4.2cm][l]{\textbf{\color{acento}#1}}#2\par\addvspace{2pt}}

% Metadatos del PDF
\AtBeginDocument{\hypersetup{pdftitle={\ar@tipodocumento\ — \ar@curso},
  pdfauthor={\ar@docente}, pdflang={es-PE}}}
\endinput
