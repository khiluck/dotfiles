
syntax on
" colors
"colorscheme solarized
"colorscheme solas


set nocompatible              " be iMproved, required
filetype off                  " required

" set the runtime path to include Vundle and initialize
set rtp+=~/.vim/bundle/Vundle.vim
call vundle#begin()

" let Vundle manage Vundle, required
Plugin 'VundleVim/Vundle.vim'
" A Vim Plugin for Lively Previewing LaTeX PDF Output
call vundle#end()



" Colorscheme gruvbox
Plugin 'morhetz/gruvbox'
autocmd vimenter * ++nested colorscheme gruvbox
set background=dark
" transparent bg
autocmd vimenter * hi Normal guibg=NONE ctermbg=NONE
" For Vim<8, replace EndOfBuffer by NonText
autocmd vimenter * hi EndOfBuffer guibg=NONE ctermbg=NONE




" Настройки табов для Python, согласно рекоммендациям
set tabstop=4 
set shiftwidth=4
set smarttab
set expandtab "Ставим табы пробелами
set softtabstop=4 "4 пробела в табе
" Автоотступ
set autoindent
" Подсвечиваем все что можно подсвечивать
let python_highlight_all = 1
" Включаем 256 цветов в терминале, мы ведь работаем из иксов?
" Нужно во многих терминалах, например в gnome-terminal
set t_Co=256

" Перед сохранением вырезаем пробелы на концах (только в .py файлах)
autocmd BufWritePre *.py normal m`:%s/\s\+$//e ``
" В .py файлах включаем умные отступы после ключевых слов
autocmd BufRead *.py set smartindent cinwords=if,elif,else,for,while,try,except,finally,def,class
 
syntax on "Включить подсветку синтаксиса
 
" set nu "Включаем нумерацию строк
"set mousehide "Спрятать курсор мыши когда набираем текст
"set mouse=a "Включить поддержку мыши
set termencoding=utf-8 "Кодировка терминала
set novisualbell "Не мигать 
set t_vb= "Не пищать! (Опции 'не портить текст', к сожалению, нету)
" Удобное поведение backspace
set backspace=indent,eol,start whichwrap+=<,>,[,]
" Вырубаем черточки на табах
set showtabline=1
 
" Переносим на другую строчку, разрываем строки
set wrap
set linebreak
 
" Вырубаем .swp и ~ (резервные) файлы
set nobackup
set noswapfile
set encoding=utf-8 " Кодировка файлов по умолчанию
set fileencodings=utf8,cp1251
 
set clipboard=unnamed
set ruler
 
set hidden
nnoremap <C-N> :bnext<CR>
nnoremap <C-P> :bprev<CR>
 
" Выключаем звук в Vim
set visualbell t_vb=
 
"set guifont=Monaco:h20
 
" Disable autoindent for paste from buffer
set paste
 
" highlights parentheses
set showmatch









" specify file formats
set fileformats=unix,dos
 
" take 50 search histories
set history=50
 
" ignore Case
set ignorecase
 
" distinct Capital if you mix it in search words
set smartcase
 
" highlights matched words
" if not, specify [ set nohlsearch ]
set hlsearch
 
" use incremental search
" if not, specify [ set noincsearch ]
set incsearch
 
" show line number
" if not, specify [ set nonumber ]
"set number
 
" Visualize break ( $ ) or tab ( ^I )
"set list
 
" not insert LF at the end of file
set binary noeol
 
" enable auto-indent
" if not, specify [ noautoindent ]
"set autoindent
 
" change colors for comments if it's set [ syntax on ]
highlight Comment ctermfg=DarkGray
 
" when you type _bash word it will translate into shebang )
abbr _bash #!/bin/bash<CR>
 