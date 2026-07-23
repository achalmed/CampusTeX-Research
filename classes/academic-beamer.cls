%% ============================================================================
%% academic-beamer.cls — Diapositivas y presentaciones (Beamer, XeLaTeX)
%% ----------------------------------------------------------------------------
%% Clase delgada sobre `beamer` que aplica el tema «Academic». Comparte la
%% identidad visual con academic-base/academic-exam (mismo styles/academic.sty,
%% cargado por el tema). Las plantillas solo hacen \documentclass{academic-beamer}.
%% Motor: XeLaTeX exclusivamente.
%%
%% Opciones: se pasan a beamer (p. ej. aspectratio=169, handout).
%% ============================================================================
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{academic-beamer}[2026/07/23 v1 Presentaciones Academic (XeLaTeX)]

\DeclareOption*{\PassOptionsToClass{\CurrentOption}{beamer}}
\ProcessOptions\relax
\LoadClass[aspectratio=169,11pt]{beamer}

\usetheme{Academic}
\endinput
