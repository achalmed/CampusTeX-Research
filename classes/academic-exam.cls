%% ============================================================================
%% academic-exam.cls — Evaluaciones (exámenes, prácticas, bancos, solucionarios)
%% ----------------------------------------------------------------------------
%% Sucesora de la antigua evaluacion.cls: hereda academic-base (identidad
%% única: fuentes, paleta, cajas, código, tablas, math) y añade SOLO lo específico
%% de evaluaciones. Preserva toda la funcionalidad y la API previa.
%% (Motor: pdfLaTeX -> XeLaTeX -> LuaLaTeX en su historia; hoy LuaLaTeX.)
%%
%% Opciones:  soluciones · claves · compacto
%% Motor: LuaLaTeX exclusivamente.
%% ============================================================================
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{academic-exam}[2026/07/23 v1 Evaluaciones Academic (LuaLaTeX)]

% ---------------------------------------------------------------- opciones ---
\newif\ifev@soluciones \ev@solucionesfalse
\newif\ifev@claves     \ev@clavesfalse
\newif\ifev@compacto   \ev@compactofalse
\DeclareOption{soluciones}{\ev@solucionestrue\ev@clavestrue}
\DeclareOption{claves}{\ev@clavestrue}
\DeclareOption{compacto}{\ev@compactotrue}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{academic-base}}
\ProcessOptions\relax
\LoadClass{academic-base}     % identidad + article + LuaLaTeX

% Paquetes extra no provistos por la base/identidad
\RequirePackage{fancyhdr}
\RequirePackage{enumitem}
\RequirePackage{tasks}
\RequirePackage{needspace}
\RequirePackage{comment}

% Alias de color: nombres previos → identidad «Academic» (sin duplicar paleta)
\colorlet{colorprimario}{acento}
\colorlet{colorsecundario}{secundario}
\colorlet{colorenfasis}{acento}
\colorlet{colorexito}{acento}
\colorlet{colornota}{secundario}
\colorlet{gristexto}{secundario}
\colorlet{grislinea}{filete}
\colorlet{grisfondo}{cajafondo}

% Geometría (compacta con la opción)
\ifev@compacto
  \geometry{a4paper,top=2.1cm,bottom=2.1cm,left=1.9cm,right=1.9cm,headheight=14pt,headsep=0.45cm,footskip=1.0cm}
\else
  \geometry{a4paper,top=2.7cm,bottom=2.7cm,left=2.4cm,right=2.4cm,headheight=14pt,headsep=0.55cm,footskip=1.15cm}
\fi
\setlength{\parskip}{0.55em plus 2pt minus 1pt}

% --------------------------------------------------------------- metadatos ---
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
\def\ev@estudiante{Achalma Mendoza, Elmer Edison}
\newcommand{\estudiante}[1]{\def\ev@estudiante{#1}}
\def\ev@codigoestudiante{}\newcommand{\codigoestudiante}[1]{\def\ev@codigoestudiante{#1}}
\def\ev@seccion{}\newcommand{\seccion}[1]{\def\ev@seccion{#1}}
\def\ev@subtitulo{}\newcommand{\subtitulo}[1]{\def\ev@subtitulo{#1}}

% ------------------------------------------------- totales (vía .aux, ×2) ---
\newcounter{pregunta}
\newdimen\ev@ptsdim \ev@ptsdim=0pt
\def\evaltotpuntos{??}
\def\evaltotpreguntas{0}
\def\evalregpts#1#2{\expandafter\gdef\csname evalpts#1\endcsname{#2}}
\AtEndDocument{%
  \immediate\write\@auxout{\string\gdef\string\evaltotpuntos{\strip@pt\ev@ptsdim}}%
  \immediate\write\@auxout{\string\gdef\string\evaltotpreguntas{\arabic{pregunta}}}}
\newcommand{\totalpuntos}{\evaltotpuntos}
\newcommand{\totalpreguntas}{\evaltotpreguntas}

% --------------------------------------------------------- encabezado/pie ---
\pagestyle{fancy}\fancyhf{}
\fancyhead[L]{{\small\scshape\color{gristexto}\ev@curso}}
\fancyhead[R]{{\small\scshape\color{gristexto}\ev@tipoevaluacion}}
\fancyfoot[C]{{\footnotesize\color{gristexto}\thepage}}
\renewcommand{\headrule}{{\color{grislinea}\hrule width\headwidth height 0.4pt}}
\renewcommand{\headrulewidth}{0.4pt}
\fancypagestyle{primera}{\fancyhf{}\renewcommand{\headrulewidth}{0pt}%
  \renewcommand{\headrule}{}\fancyfoot[C]{{\footnotesize\color{gristexto}\thepage}}}

% -------------------------------------------------------------- secciones ---
\titleformat{\section}{\large\bfseries\scshape\color{colorprimario}}{\thesection.}{0.6em}{}[{\color{grislinea}\titlerule[0.4pt]}]
\titlespacing*{\section}{0pt}{1.5em}{0.7em}
\titleformat{\subsection}{\normalsize\bfseries\scshape\color{colorprimario}}{\thesubsection.}{0.6em}{}
\titlespacing*{\subsection}{0pt}{1.1em}{0.4em}

% ================================================================ MEMBRETE ==
\newcommand{\ev@lbl}[1]{\textbf{\color{colorprimario}#1}}
\newcommand{\ev@filauna}[2]{\edef\ev@tmpval{#2}\ifdefempty{\ev@tmpval}{}{\makebox[2.4cm][l]{\ev@lbl{#1}}#2\par}}
\newcommand{\ev@campocorto}[1]{\edef\ev@tmpc{#1}\ifdefempty{\ev@tmpc}{\hrulefill}{#1}}
\newcommand{\membrete}{%
  \thispagestyle{primera}%
  \begin{minipage}[t]{0.74\textwidth}
    {\large\scshape\bfseries\color{colorprimario}\ev@universidad\par}
    \ifdefempty{\ev@facultad}{}{{\small\scshape\color{gristexto}\ev@facultad\par}}
    \ifdefempty{\ev@escuela}{}{{\small\scshape\color{gristexto}\ev@escuela\par}}
  \end{minipage}\hfill
  \begin{minipage}[t]{0.24\textwidth}\raggedleft
    \ifdefempty{\ev@logo}{{\small\scshape\color{gristexto}\ev@periodo}}{\includegraphics[height=1.5cm]{\ev@logo}}%
  \end{minipage}\par\vspace{0.55em}
  {\small\setlength{\parskip}{0.18em}\setlength{\parindent}{0pt}%
   \ev@filauna{Curso}{\ev@curso\ifdefempty{\ev@codigocurso}{}{\ \ (\ev@codigocurso)}}%
   \ev@filauna{Docente}{\ev@docente}%
   \makebox[2.4cm][l]{\ev@lbl{Estudiante}}\ev@estudiante\hfill
     \makebox[5cm][l]{\ev@lbl{Código:}\ \ev@campocorto{\ev@codigoestudiante}}\par
   \makebox[2.4cm][l]{\ev@lbl{Fecha}}\ev@fechaevaluacion\hfill
     \makebox[5cm][l]{\ifdefempty{\ev@duracion}{}{\ev@lbl{Duración:}\ \ev@duracion}}\par}%
  \vspace{0.55em}{\color{colorprimario}\hrule height 0.6pt}\vspace{0.5em}
  \begin{center}
    {\large\bfseries\scshape\color{colorprimario}\ev@tipoevaluacion\par}%
    \ifev@soluciones{\scshape\color{gristexto}Solucionario\par}\fi%
    \ifdefempty{\ev@subtitulo}{}{{\small\itshape\color{gristexto}\ev@subtitulo\par}}%
  \end{center}\vspace{0.8em}}
\newcommand{\camposidentificacion}{}

% ================================================================= PORTADA ==
\newcommand{\portada}[1][]{%
  \thispagestyle{empty}\begin{center}
    \ifdefempty{\ev@logo}{}{\includegraphics[height=2.4cm]{\ev@logo}\par\vspace{1.2em}}
    {\scshape\Large\color{colorprimario}\ev@universidad\par}\vspace{0.3em}
    \ifdefempty{\ev@facultad}{}{{\scshape\color{gristexto}\ev@facultad\par}}
    \ifdefempty{\ev@escuela}{}{{\scshape\color{gristexto}\ev@escuela\par}}\vfill
    {\color{colorprimario}\rule{0.55\textwidth}{1.1pt}\par}\vspace{1.6em}
    {\Huge\bfseries\color{colorprimario}\MakeUppercase{\ev@tipoevaluacion}\par}
    \ifev@soluciones\vspace{0.35em}{\Large\bfseries\color{colorenfasis}(Solucionario)\par}\fi
    \vspace{0.8em}{\LARGE\itshape\color{gristexto}\ev@curso\ifdefempty{\ev@codigocurso}{}{ (\ev@codigocurso)}\par}
    \ifdefempty{\ev@subtitulo}{}{\vspace{0.5em}{\large\color{colorsecundario}\ev@subtitulo\par}}
    \notblank{#1}{\vspace{0.8em}{\large\color{colorsecundario}#1\par}}{}\vspace{1.6em}
    {\color{colorprimario}\rule{0.55\textwidth}{1.1pt}\par}\vfill
    {\renewcommand{\arraystretch}{1.5}\small
     \begin{tabular}{r@{\quad}l}\multicolumn{2}{c}{}\\
       \textbf{\color{colorprimario}Docente} & \ev@docente\\
       \textbf{\color{colorprimario}Periodo} & \ev@periodo\\
       \textbf{\color{colorprimario}Fecha} & \ev@fechaevaluacion\\
       \textbf{\color{colorprimario}Modalidad} & \ev@modalidad\\
       \ifdefempty{\ev@autor}{}{\textbf{\color{colorprimario}Elaborado por} & \ev@autor\\}
     \end{tabular}\par}\vfill
    {\footnotesize\scshape\color{gristexto}\ev@periodo\par}
  \end{center}\clearpage}

% ===================================================== CUADRO DE PUNTAJES ===
\newcommand{\cuadrocalificacion}{%
  \begingroup\small\centering\renewcommand{\arraystretch}{1.5}\setlength{\tabcolsep}{7pt}%
  \def\ev@rowa{Pregunta}\def\ev@rowb{Puntaje}\def\ev@rowc{Obtenido}\count@=0
  \@whilenum\count@<\evaltotpreguntas\relax\do{\advance\count@\@ne
    \edef\ev@rowa{\ev@rowa & \the\count@}%
    \edef\ev@rowb{\ev@rowb & \ifcsname evalpts\the\count@\endcsname\csname evalpts\the\count@\endcsname\else --\fi}%
    \edef\ev@rowc{\ev@rowc & }}%
  \edef\ev@rowa{\ev@rowa & \noexpand\textbf{Total}}%
  \edef\ev@rowb{\ev@rowb & \noexpand\totalpuntos}\edef\ev@rowc{\ev@rowc & }%
  \arrayrulecolor{grislinea}%
  \begin{tabular}{|>{\bfseries\color{colorprimario}}l|*{\evaltotpreguntas}{c|}c|}
    \hline \ev@rowa \\ \hline \ev@rowb \\ \hline \ev@rowc \\[2pt] \hline\end{tabular}%
  \arrayrulecolor{black}\par\endgroup\vspace{0.8em}}

% ================================================================ PREGUNTA ==
\NewDocumentEnvironment{pregunta}{O{} o}{%
  \refstepcounter{pregunta}\needspace{4\baselineskip}\par\addvspace{1.05em}%
  \notblank{#1}{\immediate\write\@auxout{\string\evalregpts{\arabic{pregunta}}{#1}}\global\advance\ev@ptsdim by #1pt}{}%
  \noindent{\large\bfseries\color{colorprimario}Pregunta \thepregunta}%
  \IfValueT{#2}{\enskip{\normalsize\itshape\color{colorsecundario}· #2}}%
  \notblank{#1}{\hfill{\small\itshape\color{gristexto}(#1 \ifdim #1pt=1pt punto\else puntos\fi)}}{}%
  \par\nobreak\vspace{0.3em}\noindent\ignorespaces}{\par\addvspace{0.35em}}
\NewDocumentEnvironment{ejercicio}{O{} o}{%
  \refstepcounter{pregunta}\needspace{4\baselineskip}\par\addvspace{1.05em}%
  \notblank{#1}{\immediate\write\@auxout{\string\evalregpts{\arabic{pregunta}}{#1}}\global\advance\ev@ptsdim by #1pt}{}%
  \noindent{\large\bfseries\color{colorprimario}Ejercicio \thepregunta}%
  \IfValueT{#2}{\enskip{\normalsize\itshape\color{colorsecundario}· #2}}%
  \notblank{#1}{\hfill{\small\itshape\color{gristexto}(#1 \ifdim #1pt=1pt punto\else puntos\fi)}}{}%
  \par\nobreak\vspace{0.3em}\noindent\ignorespaces}{\par\addvspace{0.35em}}
\newlist{apartados}{enumerate}{3}
\setlist[apartados,1]{label=\textbf{\alph*)},leftmargin=2.1em,itemsep=5pt}
\setlist[apartados,2]{label=\roman*.,leftmargin=1.9em,itemsep=3pt}
\setlist[apartados,3]{label=\arabic*.,leftmargin=1.8em}
\newcommand{\pts}[1]{\hfill{\footnotesize\itshape\color{gristexto}(#1 p.)}}

% ================================================== PREGUNTAS OBJETIVAS =====
\NewTasks[label={\textbf{\alph*)}},label-width=1.5em,item-indent=2.1em,label-offset=0.35em,after-item-skip=3pt plus 1pt]{opciones}[\opcion](2)
\newcommand{\correcta}[1]{\ifev@claves{\bfseries\color{colorprimario}#1}\else#1\fi}
\newcommand{\clave}[1]{\ifev@claves\par\nobreak{\small\color{colorprimario}\textsc{Clave:}\ #1}\par\fi}
% Casilla V/F con iconos fontawesome (la identidad usa fontawesome; evita
% \square/\boxtimes de amssymb, incompatibles con unicode-math).
\newcommand{\ev@casillavacia}{{\color{grislinea}\faSquare[regular]}}
\newcommand{\ev@casilla}[2]{\ifev@claves\edef\ev@tmpa{#1}\edef\ev@tmpb{#2}%
  \ifx\ev@tmpa\ev@tmpb{\color{colorprimario}\faCheckSquare}\else\ev@casillavacia\fi\else\ev@casillavacia\fi}
\newcommand{\vf}[2][]{#2 & \ev@casilla{#1}{V} & \ev@casilla{#1}{F}\\\addlinespace[5pt]}
\newenvironment{tablavf}{\par\medskip\noindent
  \tabularx{\linewidth}{@{}>{\raggedright\arraybackslash}X>{\centering\arraybackslash}p{1.1cm}>{\centering\arraybackslash}p{1.1cm}@{}}%
  & {\bfseries\color{colorprimario}V} & {\bfseries\color{colorprimario}F}\\
  \addlinespace[3pt]\arrayrulecolor{grislinea}\hline\addlinespace[5pt]}{\arrayrulecolor{black}\endtabularx\par\medskip}
\newcounter{ev@emp}
\newenvironment{emparejamiento}{\setcounter{ev@emp}{0}\par\medskip\noindent
  \tabularx{\linewidth}{@{}>{\raggedright\arraybackslash}X@{\qquad}>{\raggedright\arraybackslash}X@{}}%
  {\bfseries\color{colorprimario}Columna A} & {\bfseries\color{colorprimario}Columna B}\\
  \addlinespace[3pt]\arrayrulecolor{grislinea}\hline\addlinespace[5pt]}{\arrayrulecolor{black}\endtabularx\par\medskip}
\newcommand{\pareja}[3][]{\stepcounter{ev@emp}\textbf{\arabic{ev@emp}.}~#2\hfill
  (\,\ifev@claves{\color{colorexito}\bfseries\ifblank{#1}{\hspace{1.2em}}{#1}}\else\hspace{1.2em}\fi\,) & \textbf{\alph{ev@emp})}~#3 \\ \addlinespace[5pt]}
\newcommand{\completar}[2][]{\underline{\makebox[#2]{\ifev@claves{\itshape\color{colorexito}#1}\else\strut\fi}}}

% ======================================================= ESPACIOS EN BLANCO =
\newcommand{\lineasrespuesta}[1]{\ifev@soluciones\else\par\nobreak\begingroup\count@=0
  \@whilenum\count@<#1\relax\do{\advance\count@\@ne\noindent{\color{grislinea}\rule[-0.9em]{\linewidth}{0.4pt}}\par\nobreak}\endgroup\par\fi}
\newcommand{\espaciorespuesta}[1]{\ifev@soluciones\else\vspace*{#1}\fi}
\newcommand{\recuadrorespuesta}[1]{\ifev@soluciones\else\par\medskip\noindent
  {\color{grislinea}\fbox{\parbox[t][#1][t]{\dimexpr\linewidth-2\fboxsep-2\fboxrule}{\strut}}}\par\medskip\fi}

% ================================================================ SOLUCIÓN ==
% Bloque de solución/desarrollo con el estilo de caja compartido (academicbox).
\ifev@soluciones
  \NewTColorBox{solucion}{}{academicbox, title={\textsc{Solución}}}
\else
  \excludecomment{solucion}
\fi
\NewTColorBox{desarrollo}{}{academicbox, title={\textsc{Desarrollo}}}

% Cajas informativas ({instrucciones}, {formulario}, {criterios}, {datos},
% {observacion}, {definicion}, {teorema}) y código ({codigo}, {salida}) provienen
% de la identidad compartida (styles/academic-boxes, academic-code): no se redefinen.

% ==================================================================== VARIOS =
\newcommand{\cab}[1]{{\bfseries\color{white}#1}}
\newcommand{\filacabecera}{\rowcolor{colorprimario}}
\sisetup{detect-all,group-minimum-digits=4}
\newcommand{\findelexamen}{}

% ==================================================== RESOLUCIÓN ESTRUCTURADA =
\pgfkeys{/evficha/.cd, tema/.initial={}, nivel/.initial={}, tiempo/.initial={}, competencias/.initial={}}
\newcommand{\ev@fitem}[2]{\notblank{#2}{#1:\,#2\hskip1em plus .3em minus .2em}{}}
\newcommand{\ficha}[1]{\ifev@soluciones
  \pgfkeys{/evficha/.cd, tema={}, nivel={}, tiempo={}, competencias={}, #1}%
  \par\nobreak\vspace{-0.85em}{\footnotesize\itshape\color{gristexto}%
   \ev@fitem{Nivel}{\pgfkeysvalueof{/evficha/nivel}}\ev@fitem{Tiempo}{\pgfkeysvalueof{/evficha/tiempo}}\par}\vspace{0.4em}\fi\ignorespaces}
\newcommand{\etapa}[1]{\par\addvspace{0.55em}\needspace{2.2\baselineskip}\setcounter{evpaso}{0}%
  \noindent{\small\bfseries\scshape\color{colorsecundario}#1}\par\nobreak\vspace{0.15em}\noindent\ignorespaces}
\newcounter{evpaso}[pregunta]
\newcommand{\paso}[1]{\par\addvspace{0.3em}\stepcounter{evpaso}%
  \noindent{\bfseries\color{colorprimario}Paso \theevpaso.}\enspace{\itshape\color{gristexto}#1}\par\nobreak\vspace{0.1em}\noindent\ignorespaces}
\newcommand{\aplica}[1]{\par\nobreak\vspace{0.2em}\noindent\hspace*{1.2em}%
  {\setlength{\fboxsep}{5pt}\setlength{\fboxrule}{0.4pt}\fcolorbox{grislinea}{white}{\small #1}}\par\nobreak\vspace{0.25em}\noindent\ignorespaces}
% \interpreta{...}: interpretación breve intercalada (antes \nota; renombrado para
% no chocar con la caja {nota} de la identidad compartida).
\newcommand{\interpreta}[1]{\par\nobreak\vspace{0.05em}\noindent\hspace*{1.2em}{\footnotesize\itshape\color{colorsecundario}#1}\par\nobreak\vspace{0.12em}\noindent\ignorespaces}
\newenvironment{ecua}{\par\addvspace{0.35em}\noindent\renewcommand{\arraystretch}{1.5}\setlength{\tabcolsep}{0pt}%
  \begin{tabular}{@{}>{\raggedleft\arraybackslash$\displaystyle}p{.17\hsize}<{$}@{\ }>{$\displaystyle{}}p{\dimexpr.83\hsize-1em\relax}<{$}@{}}}%
  {\end{tabular}\par\addvspace{0.35em}\noindent\ignorespaces}
\newenvironment{ecuac}{\par\addvspace{0.35em}\[\begin{gathered}}{\end{gathered}\]\par\addvspace{0.1em}\noindent\ignorespaces}
\newcommand{\respuesta}[1]{\par\addvspace{0.45em}\noindent{\bfseries\scshape\color{colorprimario}Respuesta.}\enspace #1\par\addvspace{0.35em}}

% ------------------------------------------------------- metadatos del PDF --
\AtBeginDocument{%
  \ifdefempty{\ev@autor}{\def\ev@pdfauthor{\ev@docente}}{\def\ev@pdfauthor{\ev@autor}}%
  \hypersetup{pdftitle={\ev@tipoevaluacion\ — \ev@curso}, pdfauthor={\ev@pdfauthor},
    pdfsubject={\ev@universidad\ · \ev@periodo}, pdflang={es-PE}}}
\endinput
