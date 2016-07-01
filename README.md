# BetterFindBuffer for SublimeText 3
Adds a couple of missing features to SublimeText Find Results buffer.

**Note**: You need to *restart* your SublimeText after installing this plugin.

## Features
- Open the the file and line under the cursor by pressing <kbd>Enter</kbd> or <kbd>o</kbd>
- <kbd>n</kbd> and <kbd>p</kbd> to jump to next/previous file
- <kbd>j</kbd> and <kbd>k</kbd> to jump to next/previous match
- Open multiple files with multiple cursor at the same time by selecting lines and pressing <kbd>Enter</kbd> or <kbd>o</kbd>
- Open all files in the result with <kbd>a</kbd>
- Fold a result with <kbd>f</kbd> and move to next file
- Show shortcuts with <kbd>?</kbd>
- Remove path prefix in filenames based on open sublime's project folders (can be disabled in settings)
- Set find results as readonly (can be disabled in settings)
- Adds search keyword and file names to the symbols list (use <kbd>Super</kbd>+<kbd>R</kbd>)
- Cleaner UI (hides line numbers, gutter, indent guides)
- Better Syntax highlighting for find results
- Cutom color scheme

![BetterFindBuffer Screenshot1](https://cloud.githubusercontent.com/assets/3202/16536669/d9ed24c0-3ff4-11e6-9d4f-779049c063cd.png)

![BetterFindBuffer Screenshot2](https://cloud.githubusercontent.com/assets/3202/16536672/e07db07a-3ff4-11e6-865d-1f24cb2a8dad.png)

## Installation
You can install via [Sublime Package Control](http://wbond.net/sublime_packages/package_control)
Or you can clone this repo into your Sublime Text Packages folder.

## Changing color scheme
If you don't like colors used in the find results buffer just copy [this file](https://github.com/aziz/BetterFindBuffer/blob/master/FindResults.hidden-tmTheme) to your User folder, change colors and save it and then create a file called `Find Results.sublime-settings` in your User folder and paste the code below:

``` json
{
  "color_scheme": "Path to your custom color scheme file. e.g. Packages/User/Custom_FindResults.hidden-tmTheme",
}
```

Alternatively, You can use [BetterFindBuffer-Designer](http://bobtherobot.github.io/BetterFindBuffer-Designer/) tool as GUI to easily customize the Find-Results color scheme.

### Credit
`FindInFilesOpenFileCommand` is inspired by [this answer on StackOverflow](http://stackoverflow.com/a/16779397/78254)

#### License
See the LICENSE file
