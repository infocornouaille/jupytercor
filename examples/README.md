# Examples

## tp-original.ipynb

```bash
jupytercor tp-original.ipynb --to pdf
```


```bash
LaTeX Warning: File `image.png' not found on input line 330.

! Unable to load picture or PDF file 'image.png'.
<to be read again> 
                   }
l.330 \includegraphics{image.png}
...
xdvipdfmx:fatal: Image inclusion failed. Could not find file: image.png

No output PDF file written.
```

```bash
jupytercor tp-original.ipynb -o tp-images.ipynb --images
```

```bash
Input file: tp-original.ipynb
Output file: tp-images.ipynb
Téléchargement d'images éventuelles...
image.png dans la source
image.png dans la source
image.png dans la source
image.png dans la source
image.png dans la source
Téléchargement d'images effectué avec succès !
```

```bash
jupytercor tp-images.ipynb --to pdf
```

```bash
jupytercor tp-images.ipynb -o tp-clean.ipynb --clean
```

```bash
jupytercor tp-clean.ipynb --to pdf
```

## structures-original.ipynb

```bash
jupytercor structures-original.ipynb --to pdf
```

```bash
...
! Unable to load picture or PDF file 'image1.png'.
<to be read again> 
...
```

```bash
jupytercor structures-original.ipynb -o structures-images.ipynb --images
```

```bash
jupytercor structures-images.ipynb --to pdf
```

```bash
jupytercor structures-images.ipynb -o structures-clean.ipynb --clean
```

```bash
jupytercor structures-clean.ipynb --to pdf
```
