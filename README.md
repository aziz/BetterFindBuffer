# BetterFindBuffer for SublimeText 3
Adds a couple of missing features to SublimeText Find Results buffer.

**Note**: You need to *restart* your SublimeText after installing this plugin.

## Features
- Open the the file and line under the cursor by pressing `enter`
- Easier keyboard navigation  
    `n` and `p` to jump to next/previous file 
    `j` and `k` to jump to next/previous search result
- Set find results as readonly
- Adds search keyword and file names to the symbols list (use `super+R`)
- Cleaner UI (hides line numbers, gutter, indent guides)
- Better Syntax highlighting of the find results
- Cutom color scheme

![BetterFindBuffer Screenshot](http://cl.ly/image/1t0v0L262i2U/ss2.png)

![BetterFindBuffer Screenshot2](http://cl.ly/image/1V3D29160U3E/ss.png)

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

### Credit
`FindInFilesOpenFileCommand` is inspired by [this answer on StackOverflow](http://stackoverflow.com/a/16779397/78254)

#### License
See the LICENSE file
