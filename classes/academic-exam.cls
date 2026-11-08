%% ============================================================================
%% academic-exam.cls — Evaluaciones (exámenes, prácticas, bancos, solucionarios)
%% ----------------------------------------------------------------------------
%% Sucesora de la antigua evaluacion.cls: hereda academic-base (identidad
%% única: fuentes, paleta, cajas, código, tablas, math) y añade SOLO lo específico
%% de evaluaciones. Preserva toda la funcionalidad y la API previa.
%% (Motor: pdfLaTeX -> XeLaTeX -> LuaLaTeX en su historia; hoy LuaLaTeX.)
%%
%% Opciones:  soluciones · claves · compacto · bn (= salida=bn)
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
%% Fase 6 del sistema de diseno (2026-09-20): salida en blanco y negro. La paleta
%% (config/palette.tex, GENERADA desde sistema-editorial/temas/docencia.yml) trae
%% \academicbn, que pasa los once nombres academic* a gris por luminancia y vuelve
%% a derivar los siete roles de academic-colors.sty. Se acepta `bn' y `salida=bn'.
\newif\ifev@bn \ev@bnfalse
\DeclareOption{bn}{\ev@bntrue}
\DeclareOption{salida=bn}{\ev@bntrue}
\DeclareOption{salida=pantalla}{}
\DeclareOption{salida=impresion}{}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{academic-base}}
\ProcessOptions\relax
\LoadClass{academic-base}     % identidad + article + LuaLaTeX
\ifev@bn\ifdefined\academicbn\academicbn\else\ClassWarning{academic-exam}{bn: config/palette.tex no define \string\academicbn (regenera la capa)}\fi\fi

% Paquetes extra no provistos por la base/identidad
\RequirePackage{fancyhdr}
\RequirePackage{enumitem}
\RequirePackage{tasks}
\RequirePackage{needspace}
\RequirePackage{comment}

% Marcadores del PDF: cada pregunta (o ejercicio) es una entrada del índice lateral del lector, para saltar entre ellas;
% el panel se abre solo al abrir el PDF (2026-11-08).
\hypersetup{bookmarksopen=true, bookmarksnumbered=false, pdfpagemode=UseOutlines}

% Citas en APA 7 (biblatex-apa + Biber; scripts/build.sh corre Biber si el documento cita). Las claves son las de
% Better BibTeX en Zotero, la autoridad de citas del ecosistema; el .bib es la exportación de Zotero (zotero.bib) o el
% referencias.bib que genera scripts/bib-zotero.py desde Zotero. \referencias imprime la lista solo en el solucionario y
% solo con \configuracion{referencias=true} (2026-11-08: por omisión, oculta).
\RequirePackage{csquotes}
\RequirePackage[style=apa, backend=biber]{biblatex}
\DeclareLanguageMapping{spanish}{spanish-apa}   % «y» entre autores, «Recuperado de», etc.
% APA 7 en español (manual de la APA, ed. en español): «y» antes del último autor, sin la coma inglesa, en las
% referencias y en las citas entre paréntesis.
\DeclareDelimFormat[bib,biblist]{finalnamedelim}{\addspace\bibstring{and}\space}
\DeclareDelimFormat[parencite]{finalnamedelim}{\addspace\bibstring{and}\space}
% \referencias: la lista APA al final, solo en el solucionario y si \configuracion{referencias=true} (apagada por omisión)
\newcommand{\referencias}{\ifev@soluciones\ifevc@referencias\ev@listareferencias\fi\fi}
\newcommand{\ev@listareferencias}{\pdfbookmark[0]{Referencias}{referencias}%
  \printbibliography[heading=bibintoc, title=Referencias]}

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
% el nombre y el código se escriben solo en el solucionario y si datosestudiante (por omisión); si no, líneas en blanco
\newcommand{\ev@sillenaestudiante}[2]{\ifev@soluciones\ifevc@datosestudiante#1\else#2\fi\else#2\fi}
\def\ev@codigoestudiante{09170105}   % código del estudiante por defecto (junto al nombre); solo se imprime en modo soluciones
\newcommand{\codigoestudiante}[1]{\def\ev@codigoestudiante{#1}}
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

% ================================================ CONFIGURACIÓN DEL DOCUMENTO =
% \configuracion{clave=true|false, …}: muestra u oculta cada elemento visible. Todo está activado por omisión (la
% salida de siempre). Lo edita LaTeX Studio desde config/latex-studio.yml (2026-11-08); también se escribe a mano.
%   preguntas: nivel, tiempo, puntaje        solución: etapas, numeropaso, titulopaso, aplica, interpreta, rotulorespuesta
%   cajas: instrucciones                     membrete: membrete, docente, estudiante, duracion, periodo, solucionario, subtitulo
%   página: encabezado, numeropagina       estudiante: datosestudiante     al final: referencias (false por omisión)
% Cada etapa de la solución, una a una (2026-11-08): etapadatos, etapaobjetivo, etapamarcoteorico, etapaprocedimiento,
% etapaverificacion, etapainterpretacion, etapadiscusion = visible | sin título | oculta («sin título»: el contenido sin su
% rótulo; «oculta»: ni rótulo ni contenido, hasta la siguiente \etapa, la \respuesta o el fin de la solución). La clave
% sale del título: sin tildes, espacios ni mayúsculas («Marco teórico» → marcoteorico).
\newcommand{\ev@nuevaopcion}[1]{\expandafter\newif\csname ifevc@#1\endcsname\csname evc@#1true\endcsname
  \pgfkeys{/evconfig/#1/.is if=evc@#1}}
\ev@nuevaopcion{nivel}\ev@nuevaopcion{tiempo}\ev@nuevaopcion{puntaje}
\ev@nuevaopcion{etapas}\ev@nuevaopcion{numeropaso}\ev@nuevaopcion{titulopaso}
\ev@nuevaopcion{aplica}\ev@nuevaopcion{interpreta}\ev@nuevaopcion{rotulorespuesta}
\ev@nuevaopcion{instrucciones}
\ev@nuevaopcion{membrete}\ev@nuevaopcion{docente}\ev@nuevaopcion{estudiante}\ev@nuevaopcion{duracion}
\ev@nuevaopcion{periodo}\ev@nuevaopcion{solucionario}\ev@nuevaopcion{subtitulo}
\ev@nuevaopcion{encabezado}\ev@nuevaopcion{numeropagina}
% 2026-11-08: datosestudiante=false deja en blanco el nombre y el código también en el solucionario; referencias=true
% imprime la lista APA al final del solucionario (apagada por omisión: las citas del texto bastan)
\ev@nuevaopcion{datosestudiante}\ev@nuevaopcion{referencias}\evc@referenciasfalse
\newcommand{\ev@nuevaetapa}[1]{\pgfkeys{/evconfig/etapa#1/.initial=visible}}
\ev@nuevaetapa{datos}\ev@nuevaetapa{objetivo}\ev@nuevaetapa{marcoteorico}\ev@nuevaetapa{procedimiento}
\ev@nuevaetapa{verificacion}\ev@nuevaetapa{interpretacion}\ev@nuevaetapa{discusion}
\pgfkeys{/evconfig/.unknown/.code={\ClassWarning{academic-exam}{\string\configuracion: clave desconocida
  «\pgfkeyscurrentname»}}}
\newcommand{\configuracion}[1]{\pgfkeys{/evconfig/.cd,#1}}
\AtBeginDocument{%
  \ifevc@instrucciones\else\RenewDocumentEnvironment{instrucciones}{o +b}{}{\ignorespacesafterend}\fi
  \ifevc@encabezado\else\fancyhead{}\renewcommand{\headrulewidth}{0pt}\renewcommand{\headrule}{}\fi
  \ifevc@numeropagina\else\fancyfoot{}\fancypagestyle{primera}{\fancyhf{}\renewcommand{\headrulewidth}{0pt}%
    \renewcommand{\headrule}{}}\fi}

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
\newcommand{\membrete}{\ifevc@membrete\ev@membrete\else\thispagestyle{primera}\fi}
\newcommand{\ev@membrete}{%
  \thispagestyle{primera}%
  \begin{minipage}[t]{0.74\textwidth}
    {\large\scshape\bfseries\color{colorprimario}\ev@universidad\par}
    \ifdefempty{\ev@facultad}{}{{\small\scshape\color{gristexto}\ev@facultad\par}}
    \ifdefempty{\ev@escuela}{}{{\small\scshape\color{gristexto}\ev@escuela\par}}
  \end{minipage}\hfill
  \begin{minipage}[t]{0.24\textwidth}\raggedleft
    \ifdefempty{\ev@logo}{\ifevc@periodo{\small\scshape\color{gristexto}\ev@periodo\par
      \ifdefempty{\ev@fechaevaluacion}{}{\ifdefstrequal{\ev@fechaevaluacion}{\ev@periodo}{}{\ev@fechaevaluacion\par}}}\fi}%
      {\includegraphics[height=1.5cm]{\ev@logo}}%
  \end{minipage}\par\vspace{0.55em}
  {\small\setlength{\parskip}{0.18em}\setlength{\parindent}{0pt}%
   \ev@filauna{Curso}{\ev@curso\ifdefempty{\ev@codigocurso}{}{\ \ (\ev@codigocurso)}}%
   \ifevc@docente\ev@filauna{Docente}{\ev@docente}\fi
   \ifevc@estudiante\makebox[2.4cm][l]{\ev@lbl{Estudiante}}%
     \ev@sillenaestudiante{\ev@estudiante}{\makebox[6cm][l]{\hrulefill}}\hfill
     \makebox[5cm][l]{\ev@lbl{Código:}\ \ev@sillenaestudiante{\ev@campocorto{\ev@codigoestudiante}}{\hrulefill}}\par\fi
   \ifevc@duracion\ifdefempty{\ev@duracion}{}{\makebox[2.4cm][l]{\ev@lbl{Duración}}\ev@duracion\par}\fi}%
  \vspace{0.55em}{\color{colorprimario}\hrule height 0.6pt}\vspace{0.5em}
  \begin{center}
    {\large\bfseries\scshape\color{colorprimario}\ev@tipoevaluacion\par}%
    \ifev@soluciones\ifevc@solucionario{\scshape\color{gristexto}Solucionario\par}\fi\fi%
    \ifevc@subtitulo\ifdefempty{\ev@subtitulo}{}{{\small\itshape\color{gristexto}\ev@subtitulo\par}}\fi%
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
  \pdfbookmark[0]{Pregunta \thepregunta}{pregunta.\thepregunta}%
  \notblank{#1}{\immediate\write\@auxout{\string\evalregpts{\arabic{pregunta}}{#1}}\global\advance\ev@ptsdim by #1pt}{}%
  \noindent{\large\bfseries\color{colorprimario}Pregunta \thepregunta}%
  \IfValueT{#2}{\enskip{\normalsize\itshape\color{colorsecundario}· #2}}%
  \ifevc@puntaje\notblank{#1}{\hfill{\small\itshape\color{gristexto}(#1 \ifdim #1pt=1pt punto\else puntos\fi)}}{}\fi%
  \par\nobreak\vspace{0.3em}\noindent\ignorespaces}{\par\addvspace{0.35em}}
\NewDocumentEnvironment{ejercicio}{O{} o}{%
  \refstepcounter{pregunta}\needspace{4\baselineskip}\par\addvspace{1.05em}%
  \pdfbookmark[0]{Ejercicio \thepregunta}{pregunta.\thepregunta}%
  \notblank{#1}{\immediate\write\@auxout{\string\evalregpts{\arabic{pregunta}}{#1}}\global\advance\ev@ptsdim by #1pt}{}%
  \noindent{\large\bfseries\color{colorprimario}Ejercicio \thepregunta}%
  \IfValueT{#2}{\enskip{\normalsize\itshape\color{colorsecundario}· #2}}%
  \ifevc@puntaje\notblank{#1}{\hfill{\small\itshape\color{gristexto}(#1 \ifdim #1pt=1pt punto\else puntos\fi)}}{}\fi%
  \par\nobreak\vspace{0.3em}\noindent\ignorespaces}{\par\addvspace{0.35em}}
\newlist{apartados}{enumerate}{3}
\setlist[apartados,1]{label=\textbf{\alph*)},leftmargin=2.1em,itemsep=5pt}
\setlist[apartados,2]{label=\roman*.,leftmargin=1.9em,itemsep=3pt}
\setlist[apartados,3]{label=\arabic*.,leftmargin=1.8em}
% Puntaje de subpregunta SIEMPRE pegado al margen derecho (idiom flush-right o,
% si no cabe, en su propio renglón también a la derecha), alineado con el puntaje
% de la pregunta principal. \parfillskip=0 se fija localmente y se restaura solo.
\newcommand{\pts}[1]{\ifevc@puntaje\expandafter\ev@pts\else\expandafter\@gobble\fi{#1}}
\newcommand{\ev@pts}[1]{\unskip\nobreak\hfil\penalty50\hskip1em\hbox{}\nobreak\hfil
  {\footnotesize\itshape\color{gristexto}(#1 p.)}%
  {\parfillskip=0pt\finalhyphendemerits=0\par}}

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
% Espacios de respuesta NEUTRALIZADOS: el examen va compacto (las preguntas van
% juntas). No se reserva espacio para responder: el estudiante decide la extensión
% de su respuesta en su propia hoja. Se conservan los comandos por compatibilidad
% (los .tex existentes los usan) pero no imprimen nada, en ningún modo.
\newcommand{\lineasrespuesta}[1]{}
\newcommand{\espaciorespuesta}[1]{}
\newcommand{\recuadrorespuesta}[1]{}

% ================================================================ SOLUCIÓN ==
% Bloque de solución/desarrollo: el estilo editorial compartido (academicbox: rótulo en
% versalitas y cuerpo sangrados; sin caja ni líneas), que separa el desarrollo del
% enunciado solo por tipografía y espacio (directriz visual de evaluaciones, R10).
\ifev@soluciones
  \NewTColorBox{solucion}{}{academicbox, title={\textsc{Solución}}}
  \AtEndEnvironment{solucion}{\ev@cerraretapa}     % una etapa oculta al final de la solución
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
\newcommand{\ficha}[1]{\ifevc@nivel\def\ev@hayficha{1}\else\ifevc@tiempo\def\ev@hayficha{1}\else\def\ev@hayficha{0}\fi\fi
  \ifnum\ev@hayficha=1 \expandafter\ev@ficha\else\expandafter\ev@sinficha\fi{#1}}
\newcommand{\ev@sinficha}[1]{\ignorespaces}
\newcommand{\ev@ficha}[1]{\ifev@soluciones
  \pgfkeys{/evficha/.cd, tema={}, nivel={}, tiempo={}, competencias={}, #1}%
  \par\nobreak\vspace{-0.85em}{\footnotesize\itshape\color{gristexto}%
   \ifevc@nivel\ev@fitem{Nivel}{\pgfkeysvalueof{/evficha/nivel}}\fi
   \ifevc@tiempo\ev@fitem{Tiempo}{\pgfkeysvalueof{/evficha/tiempo}}\fi\par}\vspace{0.4em}\fi\ignorespaces}
% la clave de una etapa a partir de su título (Lua: sin tildes, espacios ni mayúsculas)
\directlua{
  function ev_clave_etapa(s)
    local tildes = {["á"]="a", ["é"]="e", ["í"]="i", ["ó"]="o", ["ú"]="u", ["ü"]="u", ["ñ"]="n",
                    ["Á"]="a", ["É"]="e", ["Í"]="i", ["Ó"]="o", ["Ú"]="u", ["Ü"]="u", ["Ñ"]="n"}
    for k, v in pairs(tildes) do s = s:gsub(k, v) end
    s = s:lower():gsub("[^a-z]", "")
    tex.sprint(s)
  end}
\newcommand{\ev@claveetapa}[1]{\directlua{ev_clave_etapa("\luaescapestring{\detokenize{#1}}")}}
% una etapa oculta se compone en una caja que se descarta; se cierra en la siguiente \etapa, en \respuesta (que siempre
% se ve: la reabre después) y al terminar la solución
\newif\ifev@etapaoculta
\newbox\ev@descarte
\newcommand{\ev@abriroculta}{\global\ev@etapaocultatrue\setbox\ev@descarte\vbox\bgroup\hsize=\linewidth
  \renewenvironment{figure}[1][]{\par}{\par}\renewenvironment{table}[1][]{\par}{\par}}
\newcommand{\ev@cerraretapa}{\ifev@etapaoculta\egroup\global\ev@etapaocultafalse\fi}
\newcommand{\ev@tituloetapa}[1]{\ifevc@etapas\par\addvspace{0.55em}\needspace{2.2\baselineskip}%
  \noindent{\small\bfseries\scshape\color{colorsecundario}#1}\par\nobreak\vspace{0.15em}\noindent\else\par\fi}
\newcommand{\etapa}[1]{\ev@cerraretapa\setcounter{evpaso}{0}%
  \edef\ev@claveactual{\ev@claveetapa{#1}}%
  \pgfkeysifdefined{/evconfig/etapa\ev@claveactual}%
    {\edef\ev@estadoetapa{\pgfkeysvalueof{/evconfig/etapa\ev@claveactual}}}{\def\ev@estadoetapa{visible}}%
  \ifdefstring{\ev@estadoetapa}{oculta}{\par\ev@abriroculta}%
    {\ifdefstring{\ev@estadoetapa}{sin título}{\par\addvspace{0.35em}\noindent}{\ev@tituloetapa{#1}}}\ignorespaces}
\newcounter{evpaso}[pregunta]
\newcommand{\paso}[1]{\par\addvspace{0.3em}\stepcounter{evpaso}%
  \ifevc@numeropaso\def\ev@pasoun{1}\else\ifevc@titulopaso\def\ev@pasoun{1}\else\def\ev@pasoun{0}\fi\fi
  \ifnum\ev@pasoun=1
    \noindent\ifevc@numeropaso{\bfseries\color{colorprimario}Paso \theevpaso.}\ifevc@titulopaso\enspace\fi\fi
    \ifevc@titulopaso{\itshape\color{gristexto}#1}\fi\par\nobreak\vspace{0.1em}%
  \fi\noindent\ignorespaces}
\NewDocumentCommand{\aplica}{O{formula} m}{\ifevc@aplica\ev@aplica[#1]{#2}\fi}
% lo que se aplica en un paso (2026-11-08): \aplica[tipo]{contenido}. Un recuadro ajustado al contenido (no de margen a
% margen), centrado, con un fondo tenue y un filete fino del color de su tipo; sin rótulos: basta el nombre dentro
% («Propiedad distributiva: …», «Vieta: …»). Los colores salen de la paleta de la identidad (academicData1–4 y sus
% mezclas), así que en salida bn pasan solos a gris. Tipos: formula (por omisión) · propiedad · teorema · definicion ·
% regla (de derivación, de cálculo) · identidad · criterio (de estabilidad, de convergencia)
\RequirePackage{varwidth}
\colorlet{evaplica@formula}{academicData3}
\colorlet{evaplica@propiedad}{academicData4}
\colorlet{evaplica@teorema}{academicData2}
\colorlet{evaplica@definicion}{academicData1}
\colorlet{evaplica@regla}{academicData3!45!academicData2}          % violeta grisáceo
\colorlet{evaplica@identidad}{academicData4!55!academicData2}      % ocre
\colorlet{evaplica@criterio}{academicData3!50!academicData4}       % verde azulado
\newtcolorbox{ev@cajaaplica}[1]{enhanced, hbox, center, arc=1.5pt, boxrule=0.45pt,
  colframe=evaplica@#1!70, colback=evaplica@#1!11, left=0.75em, right=0.75em, top=0.2em, bottom=0.2em,
  before skip=0.45em, after skip=0.55em, fontupper=\small}
\newcommand{\ev@aplica}[2][formula]{\par\nobreak
  \ifcsname\string\color@evaplica@#1\endcsname\def\ev@tipoaplica{#1}\else
    \ClassWarning{academic-exam}{\string\aplica: tipo desconocido «#1» (formula, propiedad, teorema, definicion,
      regla, identidad, criterio)}\def\ev@tipoaplica{formula}\fi
  \begin{ev@cajaaplica}{\ev@tipoaplica}\begin{varwidth}{\dimexpr\linewidth-5em\relax}\centering #2\end{varwidth}%
  \end{ev@cajaaplica}\nobreak\noindent\ignorespaces}
% lo que cambia en una línea de la resolución, para verlo sin leer: \resalta{…} pinta el término que se transforma,
% \cancela{…} tacha lo que se simplifica y \razon{…} anota a la derecha, breve, por qué (en {ecua} y {sistema})
\colorlet{evcambio}{academicData2}
\newcommand{\resalta}[1]{{\color{evcambio}#1}}
% la diagonal con TikZ (la carga tcolorbox): \cancel de cancel.sty sale muy fina y no admite grosor
\newcommand{\cancela}[1]{\mathpalette\ev@cancela{#1}}
\newcommand{\ev@cancela}[2]{\tikz[baseline=(ev@c.base)]{\node[inner sep=0.4pt, outer sep=0pt] (ev@c) {$\m@th#1#2$};
  \draw[evcambio!85, line width=0.8pt] (ev@c.south west) -- (ev@c.north east);}}
\newcommand{\razon}[1]{\qquad\text{\footnotesize\itshape\color{gristexto}#1}}   % fuera de {ecua}; dentro, columna propia
% \interpreta{...}: interpretación breve intercalada (antes \nota; renombrado para
% no chocar con la caja {nota} de la identidad compartida).
\newcommand{\interpreta}[1]{\ifevc@interpreta\expandafter\ev@interpreta\else\expandafter\@gobble\fi{#1}}
\newcommand{\ev@interpreta}[1]{\par\nobreak\vspace{0.05em}\noindent{\footnotesize\itshape\color{colorsecundario}#1}\par\nobreak\vspace{0.12em}\noindent\ignorespaces}
% {ecua}: una igualdad por línea, alineada en «&=». Tres columnas (2026-11-08): el lado izquierdo, la fórmula (ancho
% natural) y las notas de \razon{…}, que en cada bloque empiezan todas a la misma altura, tras la fórmula más ancha, y
% ocupan el resto de la línea (tabularx; una nota larga se parte en su columna)
\RequirePackage{tabularx}
\newcommand{\ev@razontabla}[1]{&#1}
\newenvironment{ecua}{\par\addvspace{0.35em}\noindent\renewcommand{\arraystretch}{1.5}\setlength{\tabcolsep}{0pt}%
  \let\razon\ev@razontabla
  \tabularx{\linewidth}{@{}>{\raggedleft\arraybackslash$\displaystyle}p{.17\linewidth}<{$}@{\ }>{$\displaystyle{}}l<{$}%
    @{\hspace{2.2em}}>{\raggedright\arraybackslash\footnotesize\itshape\leavevmode\color{gristexto}}X@{}}}%
  {\endtabularx\par\addvspace{0.35em}\noindent\ignorespaces}
\newenvironment{ecuac}{\par\addvspace{0.35em}\[\begin{gathered}}{\end{gathered}\]\par\addvspace{0.1em}\noindent\ignorespaces}
\newcommand{\respuesta}[1]{\ifev@etapaoculta\ev@cerraretapa\ev@respuesta{#1}\ev@abriroculta\else\ev@respuesta{#1}\fi}
\newcommand{\ev@respuesta}[1]{\par\addvspace{0.45em}\noindent\ifevc@rotulorespuesta{\bfseries\scshape\color{colorprimario}Respuesta.}\enspace\fi #1\par\addvspace{0.35em}}

% ------------------------------------------------------- metadatos del PDF --
\AtBeginDocument{%
  \ifdefempty{\ev@autor}{\def\ev@pdfauthor{\academicauthor}}{\def\ev@pdfauthor{\ev@autor}}%
  \hypersetup{pdftitle={\ev@tipoevaluacion\ — \ev@curso}, pdfauthor={\ev@pdfauthor},
    pdfsubject={\ev@universidad\ · \ev@periodo}, pdflang={es-PE}}}
\endinput
