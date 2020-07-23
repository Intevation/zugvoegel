[![Gitpod Ready-to-Code](https://img.shields.io/badge/Gitpod-Ready--to--Code-blue?logo=gitpod)](https://gitpod.io/#https://github.com/BjoernSchilberg/zugvoegel)

# Zugvögel

- [Zugvögel](#zugvögel)
  - [Project setup](#project-setup)
    - [Compiles and hot-reloads for development](#compiles-and-hot-reloads-for-development)
    - [Compiles and minifies for production](#compiles-and-minifies-for-production)
    - [Run your tests](#run-your-tests)
    - [Lints and fixes files](#lints-and-fixes-files)
    - [Customize configuration](#customize-configuration)
  - [Tips & Tricks](#tips--tricks)
    - [Round color corners on image](#round-color-corners-on-image)
      - [Create Round Corner](#create-round-corner)
      - [Color Round Corner](#color-round-corner)
    - [Rectangle color borders on image](#rectangle-color-borders-on-image)
  - [Convert csv to geojson](#convert-csv-to-geojson)
  - [FTP connection](#ftp-connection)

## Project setup

```shell
yarn install
```

### Compiles and hot-reloads for development

```shell
yarn run serve
```

### Compiles and minifies for production

```shell
yarn run build
```

### Run your tests

```shell
yarn run test
```

### Lints and fixes files

```shell
yarn run lint
```

### Customize configuration

See [Configuration Reference](https://cli.vuejs.org/config/).

## Tips & Tricks

### Round color corners on image

#### Create Round Corner

Color Round Border

Click alpha to selection (Do this by right clicking on the thumbnail of the
layer in your layers dialog and clicking alpha to selection on your layer)
with the rounded object.

#### Color Round Corner

Edit->Stroke Selection

In the dialogue box, leave everything selected as default, and set the line
width and color.

### Rectangle color borders on image

Option 1) Rectangle Outer border

- Filter->Decor->Round Border
- Edge Radius: half of image size.
- Deselect Add drop-shadow

Option 2) Rectangle Inner border

- Select->All
- Choose color
- Edit->Stroke Selection

In the dialogue box, leave everything selected as default, and set the line
width and color.

## Convert csv to geojson

```shell
ogr2ogr -f "GeoJSON" output.geojson input.csv -oo X_POSSIBLE_NAMES=lon -oo Y_POSSIBLE_NAMES=lat -oo KEEP_GEOM_COLUMNS=NO
```

## FTP connection

```shell
ncftp -u $FTP_USER -p $FTP_PASSWORD $FTP_SERVER
```

```shell
ncftp -u $FTP_USER -p $FTP_PASSWORD ftp://$FTP_SERVER/turteltauben
```
