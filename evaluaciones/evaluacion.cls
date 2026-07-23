%% ============================================================================
%% evaluacion.cls — Clase maestra para exámenes, prácticas y evaluaciones
%% ----------------------------------------------------------------------------
%% Sistema de plantillas académicas de Edison Achalma
%% Identidad visual única para toda la colección 50-examenes-y-practicas.
%%
%% Uso:
%%   \documentclass[opciones]{evaluacion}
%%
%% Opciones de clase:
%%   soluciones : muestra los entornos {solucion} y todas las claves;
%%                suprime líneas/espacios de respuesta (modo solucionario).
%%   claves     : muestra solo las claves de preguntas objetivas
%%                (\clave, \correcta, \vf, \pareja, \completar).
%%   compacto   : márgenes y espaciados reducidos (ahorro de papel).
%%
%% Compilar con:  latexmk -pdf archivo.tex   (o pdflatex ×2, por los totales)
%% ============================================================================
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{evaluacion}[2026/07/21 v1.0 Clase para evaluaciones academicas (E. Achalma)]

% ---------------------------------------------------------------- opciones ---
\newif\ifev@soluciones \ev@solucionesfalse
\newif\ifev@claves     \ev@clavesfalse
\newif\ifev@compacto   \ev@compactofalse
\DeclareOption{soluciones}{\ev@solucionestrue\ev@clavestrue}
\DeclareOption{claves}{\ev@clavestrue}
\DeclareOption{compacto}{\ev@compactotrue}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax
\LoadClass[11pt,a4paper]{article}

% ------------------------------------------------------------- tipografía ---
\RequirePackage[T1]{fontenc}
\RequirePackage[utf8]{inputenc}
\RequirePackage[spanish,es-noshorthands]{babel}
\spanishplainpercent % evita el % «inteligente», que rompe \, en modo matemático
\RequirePackage{libertinus-type1}      % Libertinus Serif/Sans (texto)
\RequirePackage{libertinust1math}      % Libertinus Math
\RequirePackage[varqu,scaled=0.94]{inconsolata} % monoespaciada
\RequirePackage{microtype}
\linespread{1.08}

% -------------------------------------------------------------- paquetes ----
\RequirePackage{etoolbox}
\RequirePackage{xcolor}
\RequirePackage{graphicx}
\RequirePackage{geometry}
\RequirePackage{fancyhdr}
\RequirePackage{lastpage}
\RequirePackage{titlesec}
\RequirePackage{enumitem}
\RequirePackage{tasks}
\RequirePackage{amsmath,amssymb}
\RequirePackage{mathtools}
\RequirePackage{array,tabularx,booktabs,colortbl,multirow,multicol}
\RequirePackage{threeparttable}
\RequirePackage{caption}
\RequirePackage{siunitx}
\RequirePackage{listings}
\RequirePackage{framed}
\RequirePackage{comment}
\RequirePackage{needspace}
\RequirePackage{fontawesome5}
\RequirePackage[most]{tcolorbox}
\RequirePackage{csquotes}

% ---------------------------------------------------------------- paleta ----
% Paleta sobria, casi monocroma (examen formal estilo Harvard/Oxford): un único
% acento de «tinta pizarra» —casi negro— para títulos, rótulos y filetes, más
% grises tipográficos para la jerarquía secundaria. Sin colores vivos ni verde.
% Imprime idéntico en B/N.
\definecolor{colorprimario}{HTML}{1F2A37}   % tinta pizarra (acento único)
\definecolor{colorsecundario}{HTML}{5B5B5B} % gris medio (jerarquía secundaria)
\definecolor{colorenfasis}{HTML}{1F2A37}    % énfasis = misma tinta (sin 2.º color)
\definecolor{colorexito}{HTML}{1F2A37}      % claves correctas en tinta (sin verde)
\definecolor{colornota}{HTML}{5B5B5B}       % gris para observaciones
\definecolor{gristexto}{HTML}{3A3A3A}
\definecolor{grisfondo}{gray}{0.97}
\definecolor{grislinea}{gray}{0.72}

% -------------------------------------------------------------- geometría ---
\ifev@compacto
  \geometry{a4paper,top=2.1cm,bottom=2.1cm,left=1.9cm,right=1.9cm,
            headheight=14pt,headsep=0.45cm,footskip=1.0cm}
\else
  \geometry{a4paper,top=2.7cm,bottom=2.7cm,left=2.4cm,right=2.4cm,
            headheight=14pt,headsep=0.55cm,footskip=1.15cm}
\fi
\setlength{\parindent}{0pt}
\setlength{\parskip}{0.55em plus 2pt minus 1pt}
\setlist{itemsep=2pt,topsep=4pt,parsep=0pt}

% -------------------------------------------------------------- metadatos ---
% Todos con valor por defecto vacío o genérico; se fijan en el preámbulo.
\def\ev@universidad{}\newcommand{\universidad}[1]{\def\ev@universidad{#1}}
\def\ev@facultad{}\newcommand{\facultad}[1]{\def\ev@facultad{#1}}
\def\ev@escuela{}\newcommand{\escuela}[1]{\def\ev@escuela{#1}}
\def\ev@curso{}\newcommand{\curso}[1]{\def\ev@curso{#1}}
\def\ev@codigocurso{}\newcommand{\codigocurso}[1]{\def\ev@codigocurso{#1}}
\def\ev@docente{}\newcommand{\docente}[1]{\def\ev@docente{#1}}
\def\ev@periodo{}\newcommand{\periodo}[1]{\def\ev@periodo{#1}}
\def\ev@tipoevaluacion{}\newcommand{\tipoevaluacion}[1]{\def\ev@tipoevaluacion{#1}}
\def\ev@fechaevaluacion{}\newcommand{\fechaevaluacion}[1]{\def\ev@fechaevaluacion{#1}}
\def\ev@duracion{}\newcommand{\duracion}[1]{\def\ev@duracion{#1}}
\def\ev@modalidad{}\newcommand{\modalidad}[1]{\def\ev@modalidad{#1}}
\def\ev@autor{}\newcommand{\autorevaluacion}[1]{\def\ev@autor{#1}}
\def\ev@logo{}\newcommand{\logoinstitucional}[1]{\def\ev@logo{#1}}
% Estudiante por defecto (titular del sistema); se puede sobreescribir.
\def\ev@estudiante{Achalma Mendoza, Elmer Edison}
\newcommand{\estudiante}[1]{\def\ev@estudiante{#1}}
\def\ev@codigoestudiante{}\newcommand{\codigoestudiante}[1]{\def\ev@codigoestudiante{#1}}
\def\ev@seccion{}\newcommand{\seccion}[1]{\def\ev@seccion{#1}}
% Subtítulo opcional bajo el título (además del «(Solucionario)» automático).
\def\ev@subtitulo{}\newcommand{\subtitulo}[1]{\def\ev@subtitulo{#1}}

% ------------------------------------------------- totales (vía .aux, ×2) ---
\newcounter{pregunta}
\newdimen\ev@ptsdim \ev@ptsdim=0pt
\def\evaltotpuntos{??}      % los sobreescribe el .aux en la segunda pasada
\def\evaltotpreguntas{0}
\def\evalregpts#1#2{\expandafter\gdef\csname evalpts#1\endcsname{#2}}
\AtEndDocument{%
  \immediate\write\@auxout{\string\gdef\string\evaltotpuntos{\strip@pt\ev@ptsdim}}%
  \immediate\write\@auxout{\string\gdef\string\evaltotpreguntas{\arabic{pregunta}}}%
}
\newcommand{\totalpuntos}{\evaltotpuntos}
\newcommand{\totalpreguntas}{\evaltotpreguntas}

% --------------------------------------------------------- encabezado/pie ---
\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0pt}
\fancyhead[L]{{\small\scshape\color{gristexto}\ev@curso}}
\fancyhead[R]{{\small\scshape\color{gristexto}\ev@tipoevaluacion}}
\fancyhead[C]{}
% pie: solo el número de página actual, centrado (sin universidad ni total)
\fancyfoot[C]{{\footnotesize\color{gristexto}\thepage}}
% filete muy fino bajo el encabezado, en gris tenue
\fancyheadoffset{0pt}
\renewcommand{\headrule}{{\color{grislinea}\hrule width\headwidth height 0.4pt}}
\renewcommand{\headrulewidth}{0.4pt}
\fancypagestyle{primera}{% primera página: sin cabecera ni filete superior
  \fancyhf{}%
  \renewcommand{\headrulewidth}{0pt}%
  \renewcommand{\headrule}{}%
  \fancyfoot[C]{{\footnotesize\color{gristexto}\thepage}}%
}

% -------------------------------------------------------------- secciones ---
\titleformat{\section}
  {\large\bfseries\scshape\color{colorprimario}}{\thesection.}{0.6em}{}
  [{\color{grislinea}\titlerule[0.4pt]}]
\titlespacing*{\section}{0pt}{1.5em}{0.7em}
\titleformat{\subsection}
  {\normalsize\bfseries\scshape\color{colorprimario}}{\thesubsection.}{0.6em}{}
\titlespacing*{\subsection}{0pt}{1.1em}{0.4em}
\titleformat{\subsubsection}
  {\normalsize\bfseries\itshape\color{gristexto}}{\thesubsubsection.}{0.5em}{}

% ================================================================ MEMBRETE ==
% Encabezado compacto (estilo editorial minimalista): bloque institucional a la
% izquierda + periodo a la derecha; datos esenciales en formato «Campo  valor»
% (Curso, Docente, Estudiante+Código, Fecha+Duración); filete, título centrado
% con «— Solucionario» automático, filete de cierre. Todo en ~1/4 de página.
\newcommand{\ev@lbl}[1]{\textbf{\color{colorprimario}#1}}
% Fila «Etiqueta valor»; se omite por completo si el valor (ya expandido) es vacío.
\newcommand{\ev@filauna}[2]{%
  \edef\ev@tmpval{#2}%
  \ifdefempty{\ev@tmpval}{}{\makebox[2.4cm][l]{\ev@lbl{#1}}#2\par}}
% Campo con línea de relleno: si está vacío, una línea que llega hasta el borde
% derecho de su caja (que el \hfill ancla al margen, alineándola con el filete).
\newcommand{\ev@campocorto}[1]{%
  \edef\ev@tmpc{#1}%
  \ifdefempty{\ev@tmpc}{\hrulefill}{#1}}
\newcommand{\membrete}{%
  \thispagestyle{primera}%
  \begin{minipage}[t]{0.74\textwidth}
    {\large\scshape\bfseries\color{colorprimario}\ev@universidad\par}
    \ifdefempty{\ev@facultad}{}{{\small\scshape\color{gristexto}\ev@facultad\par}}
    \ifdefempty{\ev@escuela}{}{{\small\scshape\color{gristexto}\ev@escuela\par}}
  \end{minipage}\hfill
  \begin{minipage}[t]{0.24\textwidth}
    \raggedleft
    \ifdefempty{\ev@logo}{{\small\scshape\color{gristexto}\ev@periodo}}%
                         {\includegraphics[height=1.5cm]{\ev@logo}}%
  \end{minipage}\par
  \vspace{0.55em}
  {\small
   \setlength{\parskip}{0.18em}\setlength{\parindent}{0pt}%
   \ev@filauna{Curso}{\ev@curso\ifdefempty{\ev@codigocurso}{}{\ \ (\ev@codigocurso)}}%
   \ev@filauna{Docente}{\ev@docente}%
   % columna derecha de ancho fijo → «Código:» y «Duración:» quedan alineados
   \makebox[2.4cm][l]{\ev@lbl{Estudiante}}\ev@estudiante\hfill
     \makebox[5cm][l]{\ev@lbl{Código:}\ \ev@campocorto{\ev@codigoestudiante}}\par
   \makebox[2.4cm][l]{\ev@lbl{Fecha}}\ev@fechaevaluacion\hfill
     \makebox[5cm][l]{\ifdefempty{\ev@duracion}{}{\ev@lbl{Duración:}\ \ev@duracion}}\par
  }%
  \vspace{0.55em}
  {\color{colorprimario}\hrule height 0.6pt}
  \vspace{0.5em}
  \begin{center}
    {\large\bfseries\scshape\color{colorprimario}\ev@tipoevaluacion\par}%
    \ifev@soluciones{\scshape\color{gristexto}Solucionario\par}\fi%
    \ifdefempty{\ev@subtitulo}{}{{\small\itshape\color{gristexto}\ev@subtitulo\par}}%
  \end{center}
  \vspace{0.8em}
}

% \camposidentificacion — obsoleto: los datos del estudiante ahora van en el
% \membrete. Se mantiene como orden nula por compatibilidad con archivos viejos.
\newcommand{\camposidentificacion}{}

% ================================================================= PORTADA ==
% \portada[descriptor] — carátula completa (solucionarios, expedientes, bancos)
\newcommand{\portada}[1][]{%
  \thispagestyle{empty}%
  \begin{center}
    \ifdefempty{\ev@logo}{}{\includegraphics[height=2.4cm]{\ev@logo}\par\vspace{1.2em}}
    {\scshape\Large\color{colorprimario}\ev@universidad\par}
    \vspace{0.3em}
    \ifdefempty{\ev@facultad}{}{{\scshape\color{gristexto}\ev@facultad\par}}
    \ifdefempty{\ev@escuela}{}{{\scshape\color{gristexto}\ev@escuela\par}}
    \vfill
    {\color{colorprimario}\rule{0.55\textwidth}{1.1pt}\par}
    \vspace{1.6em}
    {\Huge\bfseries\color{colorprimario}\MakeUppercase{\ev@tipoevaluacion}\par}
    \ifev@soluciones
      \vspace{0.35em}{\Large\bfseries\color{colorenfasis}(Solucionario)\par}%
    \fi
    \vspace{0.8em}
    {\LARGE\itshape\color{gristexto}\ev@curso
      \ifdefempty{\ev@codigocurso}{}{ (\ev@codigocurso)}\par}
    \ifdefempty{\ev@subtitulo}{}{\vspace{0.5em}{\large\color{colorsecundario}\ev@subtitulo\par}}
    \notblank{#1}{\vspace{0.8em}{\large\color{colorsecundario}#1\par}}{}
    \vspace{1.6em}
    {\color{colorprimario}\rule{0.55\textwidth}{1.1pt}\par}
    \vfill
    {\renewcommand{\arraystretch}{1.5}\small
     \begin{tabular}{r@{\quad}l}
       \multicolumn{2}{c}{}\\
       \textbf{\color{colorprimario}Docente}   & \ev@docente\\
       \textbf{\color{colorprimario}Periodo}   & \ev@periodo\\
       \textbf{\color{colorprimario}Fecha}     & \ev@fechaevaluacion\\
       \textbf{\color{colorprimario}Modalidad} & \ev@modalidad\\
       \ifdefempty{\ev@autor}{}{\textbf{\color{colorprimario}Elaborado por} & \ev@autor\\}
     \end{tabular}\par}
    \vfill
    {\footnotesize\scshape\color{gristexto}\ev@periodo\par}
  \end{center}
  \clearpage
}

% ===================================================== CUADRO DE PUNTAJES ===
% \cuadrocalificacion — tabla Pregunta/Puntaje/Obtenido generada
% automáticamente a partir de los puntos declarados (segunda pasada).
\newcommand{\cuadrocalificacion}{%
  \begingroup
  \small\centering
  \renewcommand{\arraystretch}{1.5}%
  \setlength{\tabcolsep}{7pt}%
  \def\ev@rowa{Pregunta}%
  \def\ev@rowb{Puntaje}%
  \def\ev@rowc{Obtenido}%
  \count@=0
  \@whilenum\count@<\evaltotpreguntas\relax\do{%
    \advance\count@\@ne
    \edef\ev@rowa{\ev@rowa & \the\count@}%
    \edef\ev@rowb{\ev@rowb &
      \ifcsname evalpts\the\count@\endcsname
        \csname evalpts\the\count@\endcsname\else --\fi}%
    \edef\ev@rowc{\ev@rowc & }%
  }%
  \edef\ev@rowa{\ev@rowa & \noexpand\textbf{Total}}%
  \edef\ev@rowb{\ev@rowb & \noexpand\totalpuntos}%
  \edef\ev@rowc{\ev@rowc & }%
  \arrayrulecolor{grislinea}%
  \begin{tabular}{|>{\bfseries\color{colorprimario}}l|*{\evaltotpreguntas}{c|}c|}
    \hline \ev@rowa \\ \hline \ev@rowb \\ \hline \ev@rowc \\[2pt] \hline
  \end{tabular}%
  \arrayrulecolor{black}%
  \par\endgroup\vspace{0.8em}}

% ================================================================ PREGUNTA ==
% \begin{pregunta}[puntos][tema]  ...  \end{pregunta}
\NewDocumentEnvironment{pregunta}{O{} o}{%
  \refstepcounter{pregunta}%
  \needspace{4\baselineskip}%
  \par\addvspace{1.05em}%
  \notblank{#1}{%
    \immediate\write\@auxout{\string\evalregpts{\arabic{pregunta}}{#1}}%
    \global\advance\ev@ptsdim by #1pt
  }{}%
  \noindent
  {\large\bfseries\color{colorprimario}Pregunta \thepregunta}%
  \IfValueT{#2}{\enskip{\normalsize\itshape\color{colorsecundario}· #2}}%
  \notblank{#1}{\hfill{\small\itshape\color{gristexto}(#1 \ifdim #1pt=1pt punto\else puntos\fi)}}{}%
  \par\nobreak\vspace{0.3em}\noindent\ignorespaces
}{\par\addvspace{0.35em}}

% Igual que pregunta, pero rotulado «Ejercicio» (prácticas y bancos)
\NewDocumentEnvironment{ejercicio}{O{} o}{%
  \refstepcounter{pregunta}%
  \needspace{4\baselineskip}%
  \par\addvspace{1.05em}%
  \notblank{#1}{%
    \immediate\write\@auxout{\string\evalregpts{\arabic{pregunta}}{#1}}%
    \global\advance\ev@ptsdim by #1pt
  }{}%
  \noindent
  {\large\bfseries\color{colorprimario}Ejercicio \thepregunta}%
  \IfValueT{#2}{\enskip{\normalsize\itshape\color{colorsecundario}· #2}}%
  \notblank{#1}{\hfill{\small\itshape\color{gristexto}(#1 \ifdim #1pt=1pt punto\else puntos\fi)}}{}%
  \par\nobreak\vspace{0.3em}\noindent\ignorespaces
}{\par\addvspace{0.35em}}

% apartados a), b), c) — con subapartados i., ii., iii.
\newlist{apartados}{enumerate}{3}
\setlist[apartados,1]{label=\textbf{\alph*)},leftmargin=2.1em,itemsep=5pt}
\setlist[apartados,2]{label=\roman*.,leftmargin=1.9em,itemsep=3pt}
\setlist[apartados,3]{label=\arabic*.,leftmargin=1.8em}
% puntos de un apartado: \item Enunciado... \pts{2}
\newcommand{\pts}[1]{\hfill{\footnotesize\itshape\color{gristexto}(#1 p.)}}

% ================================================== PREGUNTAS OBJETIVAS =====
% Opción múltiple: \begin{opciones}(n columnas) \opcion ... \end{opciones}
\NewTasks[label={\textbf{\alph*)}},label-width=1.5em,item-indent=2.1em,
          label-offset=0.35em,after-item-skip=3pt plus 1pt]{opciones}[\opcion](2)
% marca la alternativa correcta (visible solo con claves/soluciones)
\newcommand{\correcta}[1]{%
  \ifev@claves{\bfseries\color{colorprimario}#1}\else#1\fi}
% clave al pie de la pregunta (sobria: versalitas de tinta, sin icono ni color)
\newcommand{\clave}[1]{%
  \ifev@claves\par\nobreak{\small\color{colorprimario}%
    \textsc{Clave:}\ #1}\par\fi}

% Verdadero/Falso: \begin{tablavf} \vf[V]{Enunciado} ... \end{tablavf}
\newcommand{\ev@casilla}[2]{%
  \ifev@claves
    \edef\ev@tmpa{#1}\edef\ev@tmpb{#2}%
    \ifx\ev@tmpa\ev@tmpb{\color{colorprimario}$\boxtimes$}%
    \else{\color{grislinea}$\square$}\fi
  \else{\color{grislinea}$\square$}\fi}
\newcommand{\vf}[2][]{#2 & \ev@casilla{#1}{V} & \ev@casilla{#1}{F}\\\addlinespace[5pt]}
\newenvironment{tablavf}{%
  \par\medskip\noindent
  \tabularx{\linewidth}{@{}>{\raggedright\arraybackslash}X
                        >{\centering\arraybackslash}p{1.1cm}
                        >{\centering\arraybackslash}p{1.1cm}@{}}%
  & {\bfseries\color{colorprimario}V} & {\bfseries\color{colorprimario}F}\\
  \addlinespace[3pt]\arrayrulecolor{grislinea}\hline\addlinespace[5pt]
}{\arrayrulecolor{black}\endtabularx\par\medskip}

% Emparejamiento: \begin{emparejamiento} \pareja[c]{Concepto}{Definición} ...
\newcounter{ev@emp}
\newenvironment{emparejamiento}{%
  \setcounter{ev@emp}{0}\par\medskip\noindent
  \tabularx{\linewidth}{@{}>{\raggedright\arraybackslash}X@{\qquad}
                        >{\raggedright\arraybackslash}X@{}}%
  {\bfseries\color{colorprimario}Columna A} &
  {\bfseries\color{colorprimario}Columna B}\\
  \addlinespace[3pt]\arrayrulecolor{grislinea}\hline\addlinespace[5pt]
}{\arrayrulecolor{black}\endtabularx\par\medskip}
\newcommand{\pareja}[3][]{%
  \stepcounter{ev@emp}%
  \textbf{\arabic{ev@emp}.}~#2\hfill
  (\,\ifev@claves{\color{colorexito}\bfseries
      \ifblank{#1}{\hspace{1.2em}}{#1}}\else\hspace{1.2em}\fi\,)
  & \textbf{\alph{ev@emp})}~#3 \\ \addlinespace[5pt]}

% Completar espacios: \completar[respuesta]{ancho}
\newcommand{\completar}[2][]{%
  \underline{\makebox[#2]{\ifev@claves{\itshape\color{colorexito}#1}\else\strut\fi}}}

% ======================================================= ESPACIOS EN BLANCO =
% (se suprimen automáticamente en modo soluciones)
\newcommand{\lineasrespuesta}[1]{%
  \ifev@soluciones\else
    \par\nobreak\begingroup
    \count@=0
    \@whilenum\count@<#1\relax\do{%
      \advance\count@\@ne
      \noindent{\color{grislinea}\rule[-0.9em]{\linewidth}{0.4pt}}\par\nobreak}%
    \endgroup\par
  \fi}
\newcommand{\espaciorespuesta}[1]{\ifev@soluciones\else\vspace*{#1}\fi}
\newcommand{\recuadrorespuesta}[1]{%
  \ifev@soluciones\else
    \par\medskip\noindent
    {\color{grislinea}\fbox{\parbox[t][#1][t]{\dimexpr\linewidth-2\fboxsep-2\fboxrule}{\strut}}}%
    \par\medskip
  \fi}

% ================================================================ SOLUCIÓN ==
% \begin{solucion} ... \end{solucion}
% Bloque diferenciado del enunciado: fondo gris muy tenue, filete lateral
% azul y rótulo «Solución» en burdeos; el cuerpo va en gris para separarlo
% visualmente del enunciado (negro). Admite código/verbatim (breakable).
\ifev@soluciones
  \NewTColorBox{solucion}{}{%
    enhanced,breakable,sharp corners,frame hidden,
    colback=black!3,
    left=9pt,right=9pt,top=6pt,bottom=6pt,
    before skip=0.85em,after skip=0.85em,
    fontupper=\normalcolor,
    before upper={{\bfseries\scshape\color{colorprimario}Solución}%
                  \par\nobreak\vspace{2.5pt}}}
\else
  \excludecomment{solucion}
\fi
% Variante siempre visible (prácticas dirigidas con desarrollo modelo)
\NewTColorBox{desarrollo}{}{%
  enhanced,breakable,sharp corners,frame hidden,
  colback=black!3,
  left=9pt,right=9pt,top=6pt,bottom=6pt,
  before skip=0.85em,after skip=0.85em,
  fontupper=\normalcolor,
  before upper={{\bfseries\scshape\color{colorprimario}Desarrollo}%
                \par\nobreak\vspace{2.5pt}}}

% ============================================================ BLOQUES TCB ===
% Estilo sobrio compartido: filete fino gris, fondo blanco, esquinas rectas,
% SIN barra de título de color ni iconos. El rótulo va en versalitas de tinta
% sobre el cuerpo (mediante «before upper»), como el bloque de solución.
\tcbset{ev@base/.style={
  enhanced,breakable,sharp corners,boxrule=0.4pt,
  colframe=grislinea,colback=white,
  left=9pt,right=9pt,top=7pt,bottom=7pt,
  before skip=1.0em,after skip=1.0em,
  fontupper=\normalcolor}}
\newcommand{\ev@cajarotulo}[1]{%
  {\bfseries\scshape\color{colorprimario}#1}\par\nobreak\vspace{3pt}}

\NewTColorBox{instrucciones}{O{Instrucciones}}{ev@base,
  before upper={\ev@cajarotulo{#1}}}

\NewTColorBox{observacion}{O{Observación}}{ev@base,
  before upper={\ev@cajarotulo{#1}}}

\NewTColorBox{datos}{O{Datos}}{ev@base,
  before upper={\ev@cajarotulo{#1}}}

\NewTColorBox{formulario}{O{Formulario}}{ev@base,
  before upper={\ev@cajarotulo{#1}}}

\NewTColorBox{criterios}{O{Criterios de evaluación}}{ev@base,
  before upper={\ev@cajarotulo{#1}}}

% Definición / Teorema numerados, con título opcional
\NewTColorBox[auto counter]{definicion}{o}{ev@base,
  before upper={\ev@cajarotulo{Definición~\thetcbcounter%
    \IfValueT{#1}{\ \normalfont\itshape(#1)}}}}
\NewTColorBox[auto counter]{teorema}{o}{ev@base,
  before upper={\ev@cajarotulo{Teorema~\thetcbcounter%
    \IfValueT{#1}{\ \normalfont\itshape(#1)}}}}

% =================================================================== CÓDIGO =
\lstdefinelanguage{Stata}{
  morekeywords={use,clear,generate,gen,replace,egen,summarize,sum,describe,
    regress,reg,predict,test,estat,tabulate,tab,graph,twoway,scatter,line,
    import,export,delimited,save,merge,append,sort,gsort,drop,keep,if,in,
    by,bysort,foreach,forvalues,local,global,display,di,label,rename,
    logit,probit,ivregress,xtreg,xtset,tsset,areg,margins,outreg2,esttab},
  sensitive=true,
  morecomment=[l]{//},morecomment=[l]{*},morecomment=[s]{/*}{*/},
  morestring=[b]",morestring=[b]',
}
\lstset{
  basicstyle=\ttfamily\small,
  keywordstyle=\color{colorprimario}\bfseries,
  commentstyle=\color{gristexto!80}\itshape,
  stringstyle=\color{colorenfasis},
  numberstyle=\tiny\color{grislinea},
  numbers=left,numbersep=8pt,
  breaklines=true,breakatwhitespace=true,
  showstringspaces=false,tabsize=2,
  frame=single,rulecolor=\color{grislinea},
  backgroundcolor=\color{grisfondo},
  aboveskip=0.9em,belowskip=0.9em,
  literate={á}{{\'a}}1 {é}{{\'e}}1 {í}{{\'\i}}1 {ó}{{\'o}}1 {ú}{{\'u}}1
           {ñ}{{\~n}}1 {Á}{{\'A}}1 {É}{{\'E}}1 {Í}{{\'I}}1 {Ó}{{\'O}}1
           {Ú}{{\'U}}1 {Ñ}{{\~N}}1 {¿}{{?`}}1 {¡}{{!`}}1
           {ü}{{\"u}}1 {Ü}{{\"U}}1 {ö}{{\"o}}1 {Ö}{{\"O}}1
           {ä}{{\"a}}1 {Ä}{{\"A}}1 {ç}{{\c c}}1,
}
% \begin{codigo}[language=R] ... \end{codigo}
\lstnewenvironment{codigo}[1][]{\lstset{#1}}{}
% \begin{salida} ... \end{salida}  — salida de consola, sin resaltado
\lstnewenvironment{salida}[1][]{%
  \lstset{language={},numbers=none,frame=leftline,
          rulecolor=\color{grislinea},basicstyle=\ttfamily\footnotesize,#1}}{}

% ==================================================================== VARIOS =
% cabecera de tabla en color institucional: \cab{Texto}
\newcommand{\cab}[1]{{\bfseries\color{white}#1}}
\newcommand{\filacabecera}{\rowcolor{colorprimario}}
% tablas y figuras
\captionsetup{font=small,labelfont={bf,color=colorprimario},labelsep=period}
\sisetup{detect-all,group-minimum-digits=4}
% cierre del examen: sin rótulo «fin de la evaluación» (a pedido del usuario);
% se conserva como orden nula por compatibilidad con los archivos existentes.
\newcommand{\findelexamen}{}

% ==================================================== RESOLUCIÓN ESTRUCTURADA =
% API para resoluciones de calidad académica (proceso + resultado).
% Uso típico dentro de una pregunta:
%   \ficha{tema=..., nivel=..., tiempo=..., competencias=...}   (solo en modo soluciones)
%   <enunciado> ... \begin{solucion}
%     \etapa{Datos} ...      \etapa{Objetivo} ...   \etapa{Marco teórico} ...
%     \etapa{Procedimiento}  \paso{...} ... \paso{...} ...
%     \respuesta{...}
%     \etapa{Interpretación} ...   \etapa{Verificación} ...   \etapa{Discusión} ...
%   \end{solucion}

% --- Ficha de identificación de la pregunta (visible solo en solucionario) ---
\pgfkeys{/evficha/.cd,
  tema/.initial={}, nivel/.initial={}, tiempo/.initial={}, competencias/.initial={}}
% La ficha es una sola línea muy sutil: solo «Nivel · Tiempo». Las claves «tema»
% y «competencias» se aceptan por compatibilidad pero NO se muestran.
\newcommand{\ev@fitem}[2]{\notblank{#2}{#1:\,#2\hskip1em plus .3em minus .2em}{}}
\newcommand{\ficha}[1]{%
  \ifev@soluciones
    \pgfkeys{/evficha/.cd, tema={}, nivel={}, tiempo={}, competencias={}, #1}%
    \par\nobreak\vspace{-0.85em}%   pega la ficha al título del ejercicio
    {\footnotesize\itshape\color{gristexto}%
     \ev@fitem{Nivel}{\pgfkeysvalueof{/evficha/nivel}}%
     \ev@fitem{Tiempo}{\pgfkeysvalueof{/evficha/tiempo}}%
     \par}%
    \vspace{0.4em}%
  \fi\ignorespaces}

% --- Etapa: subtítulo estructural de la resolución (Datos, Objetivo, ...) -----
% Cada etapa reinicia la numeración de pasos (así cada bloque empieza en Paso 1).
\newcommand{\etapa}[1]{%
  \par\addvspace{0.55em}\needspace{2.2\baselineskip}%
  \setcounter{evpaso}{0}%
  \noindent{\small\bfseries\scshape\color{colorsecundario}#1}%
  \par\nobreak\vspace{0.15em}\noindent\ignorespaces}

% --- Paso numerado dentro del Procedimiento (reinicia en cada etapa) ----------
\newcounter{evpaso}[pregunta]
% Usa \stepcounter (no \refstepcounter): no necesitamos \ref a los pasos y así
% evitamos destinos hyperref duplicados (evpaso se reinicia en cada etapa).
\newcommand{\paso}[1]{%
  \par\addvspace{0.3em}\stepcounter{evpaso}%
  \noindent{\bfseries\color{colorprimario}Paso \theevpaso.}%
  \enspace{\itshape\color{gristexto}#1}%
  \par\nobreak\vspace{0.1em}\noindent\ignorespaces}

% --- \aplica{...}: fórmula/concepto/teorema aplicado, en recuadro evidente ----
% Recuadro sobrio de otro color (sin flecha ni etiqueta): se ve que es una fórmula.
\newcommand{\aplica}[1]{%
  \par\nobreak\vspace{0.2em}%
  \noindent\hspace*{1.2em}%
  {\setlength{\fboxsep}{5pt}\setlength{\fboxrule}{0.4pt}%
   \fcolorbox{grislinea}{white}{%
     \small #1}}%
  \par\nobreak\vspace{0.25em}\noindent\ignorespaces}

% --- \nota{...}: interpretación breve intercalada en el procedimiento --------
\newcommand{\nota}[1]{%
  \par\nobreak\vspace{0.05em}%
  \noindent\hspace*{1.2em}{\footnotesize\itshape\color{colorsecundario}#1}%
  \par\nobreak\vspace{0.12em}\noindent\ignorespaces}

% --- Entorno {ecua}: cadena de igualdades del procedimiento -------------------
% El signo = queda anclado a UN CUARTO de la caja de texto desde la izquierda,
% en la misma columna para todos los pasos: el lado izquierdo se alinea a la
% derecha hasta ese punto y el = (con el lado derecho) arranca ahí. Si el lado
% izquierdo es más ancho que 1/4, sobresale hacia la izquierda (excepción).
% Solo para UNA igualdad por línea. Uso: LHS &= RHS \\ &= RHS \\ &= RHS .
\newenvironment{ecua}{%
  \par\addvspace{0.35em}\noindent
  \renewcommand{\arraystretch}{1.5}%
  \setlength{\tabcolsep}{0pt}%
  \begin{tabular}{@{}>{\raggedleft\arraybackslash$\displaystyle}p{.17\hsize}<{$}@{\ }>{$\displaystyle{}}p{\dimexpr.83\hsize-1em\relax}<{$}@{}}%
}{\end{tabular}\par\addvspace{0.35em}\noindent\ignorespaces}

% --- Entorno {ecuac}: ecuaciones CENTRADAS (sin alineación) -------------------
% Para cuando en una línea hay dos o más igualdades, o dos o más ecuaciones
% (sistemas, pares de definiciones): van centradas, no alineadas por el =.
% Uso:  \begin{ecuac} eq1 \\ eq2 \end{ecuac}   (cada línea centrada)
\newenvironment{ecuac}{%
  \par\addvspace{0.35em}\[\begin{gathered}}%
  {\end{gathered}\]\par\addvspace{0.1em}\noindent\ignorespaces}

% --- Respuesta final destacada (sobrio, una línea o ecuación breve) ----------
\newcommand{\respuesta}[1]{%
  \par\addvspace{0.45em}\noindent
  {\bfseries\scshape\color{colorprimario}Respuesta.}\enspace #1%
  \par\addvspace{0.35em}}

% ------------------------------------------------------- hyperref (último) --
\RequirePackage[colorlinks=true,linkcolor=colorprimario,
  citecolor=colorsecundario,urlcolor=colorsecundario]{hyperref}
% pdfauthor = autor de la evaluación (\autorevaluacion) si se fijó; si no, el docente.
\AtBeginDocument{%
  \ifdefempty{\ev@autor}{\def\ev@pdfauthor{\ev@docente}}{\def\ev@pdfauthor{\ev@autor}}%
  \hypersetup{
    pdftitle={\ev@tipoevaluacion\ — \ev@curso},
    pdfauthor={\ev@pdfauthor},
    pdfsubject={\ev@universidad\ · \ev@periodo},
    pdflang={es-PE}}}

\endinput
