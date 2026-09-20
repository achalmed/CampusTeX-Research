%% ============================================================================
%% academic-beamer.cls — Diapositivas y presentaciones (Beamer, LuaLaTeX)
%% ----------------------------------------------------------------------------
%% Clase delgada sobre `beamer` que aplica el tema «Academic». Comparte la
%% identidad visual con academic-base/academic-exam (mismo styles/academic.sty,
%% cargado por el tema). Las plantillas solo hacen \documentclass{academic-beamer}.
%% Motor: LuaLaTeX exclusivamente.
%%
%% Opciones: bn (= salida=bn): la paleta en gris por luminancia (\academicbn de
%% config/palette.tex, GENERADO desde sistema-editorial/temas/docencia.yml; Fase 7,
%% 2026-09-20); las demas se pasan a beamer (p. ej. aspectratio=169, handout).
%% ============================================================================
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{academic-beamer}[2026/07/23 v1 Presentaciones Academic (LuaLaTeX)]

\newif\ifab@bn \ab@bnfalse
\DeclareOption{bn}{\ab@bntrue}
\DeclareOption{salida=bn}{\ab@bntrue}
\DeclareOption{salida=pantalla}{}
\DeclareOption{salida=impresion}{}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{beamer}}
\ProcessOptions\relax
\LoadClass[aspectratio=169,11pt]{beamer}

\usetheme{academic}
%% Con bn, los siete roles que el tema Beamer lee por nombre (acento, textoprincipal, secundario…)
%% se vuelven a derivar en gris DESPUES de cargar el tema: beamer resuelve los nombres de xcolor al usarlos.
\ifab@bn\ifdefined\academicbn\academicbn\else\ClassWarning{academic-beamer}{bn: config/palette.tex no define \string\academicbn (regenera la capa)}\fi\fi
\endinput
