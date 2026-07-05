%% Copyright 2016 Christophe Roger
%
% Author:
% Christophe Roger (Darwiin)
% Adaptado para XeLaTeX por Edison Achalma 2026
%
% This work may be distributed and/or modified under the
% conditions of the LaTeX Project Public License, either version 1.3c
% of this license or (at your option) any later version.

\ProvidesClass{yaac-xelatex}[2026/01/10 v3.0.0 'YAAC: XeLaTeX Awesome CV' Class]

\def\@@ptsize{11pt}

\DeclareOption{10pt}{\def\@@ptsize{10pt}}
\DeclareOption{11pt}{\def\@@ptsize{11pt}}
\DeclareOption{12pt}{\def\@@ptsize{12pt}}

\ProcessOptions\relax

\LoadClass[a4paper,\@@ptsize]{article}

\newif\if@showLinks   \@showLinksfalse
\newif\if@isCompact   \@isCompactfalse

% Opciones de color
\DeclareOption{green}{\def\@green{green}}
\DeclareOption{red}{\def\@red{red}}
\DeclareOption{indigo}{\def\@indigo{indigo}}
\DeclareOption{orange}{\def\@orange{orange}}
\DeclareOption{monochrome}{\def\@monochrome{monochrome}}
\DeclareOption{localFont}{\def\@local{local}}
\DeclareOption{alternative}{\def\@alternative{alternate}}
\DeclareOption{showLinks}{\@showLinkstrue}
\DeclareOption{compact}{\@isCompacttrue}

\ProcessOptions

% ============= PAQUETES PARA XeLaTeX =============
\RequirePackage{ifxetex}
\RequirePackage{xltxtra}
\RequirePackage{fontspec}
\RequirePackage{xunicode}

% Fuentes modernas para XeLaTeX
\defaultfontfeatures{Mapping=tex-text}
\setmainfont{TeX Gyre Termes}
\setsansfont{TeX Gyre Heros}
\setmonofont{TeX Gyre Cursor}

% Paquetes estándar
\RequirePackage{polyglossia}
\setdefaultlanguage{spanish}
\setotherlanguage{english}

\RequirePackage{parskip}
\RequirePackage{xcolor}
\RequirePackage{fullpage}
% Geometry se configurará en el documento principal
\RequirePackage{hyperref}
\RequirePackage{titlesec}
\RequirePackage{array}
\RequirePackage{enumitem}
\RequirePackage{longtable}
\RequirePackage{etoolbox}
\RequirePackage{tikz}
\RequirePackage[skins]{tcolorbox}
\RequirePackage{fancyhdr}
\RequirePackage{ifthen}

% Colores base
\definecolor{basecolor}{HTML}{000066}

\ifundef{\@green}{
	\ifundef{\@red}{
		\ifundef{\@indigo}{
			\ifundef{\@orange}{
				\ifundef{\@monochrome}{}
				{\definecolor{basecolor}{HTML}{000000}}
			}
			{\definecolor{basecolor}{HTML}{e68a00}}
		}
		{\definecolor{basecolor}{HTML}{3F51B5}}
	}
	{\definecolor{basecolor}{HTML}{C62828}}
}
{\definecolor{basecolor}{HTML}{006400}}

% Colores adicionales
\definecolor{darkGrey}{HTML}{989898}
\colorlet{lightGrey}{black!20}
\colorlet{sectionColor}{basecolor}
\colorlet{subsectionColor}{basecolor!80}

% Configuración de hipervínculos
\hypersetup{
	breaklinks=true,
	colorlinks=false,
	pdfborder={0 0 0}
}

\if@showLinks
\hypersetup{
	colorlinks=true,
	urlcolor=basecolor
}
\fi

% Estilos de sección
\titleformat{\section}
{\Large\raggedright\color{sectionColor}}
{}{0em}
{}
[\titlerule]

\titleformat{\subsection}
{\large\raggedright\color{subsectionColor}}
{}{0em}
{}

% Comandos personalizados
\newcommand{\icontextcls}[2]{%
	\mbox{%
		\textcolor{basecolor}{#1}\hspace{0.2em}%
		{#2}%
	}%
}

\newcommand{\icon}[1]{%
	\textcolor{basecolor}{#1}%
}

% Entornos personalizados
\newenvironment{contenido}{%
	\begin{flushleft}
	}{%
	\end{flushleft}
}

\endinput