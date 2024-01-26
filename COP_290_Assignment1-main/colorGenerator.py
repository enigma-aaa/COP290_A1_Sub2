import random
arr =['#d04848','#f3b95f',
    '#6895d2',
    '#37b5b6',
    '#ff6868',
    '#ff9843',
    '#ff004d',
    '#dc84f3',
    '#ffb534',
    '#711db0',
    '#527853',
    '#ee7214',
    '#31304d',
    '#0766ad',
    '#a3b763',
    '#fa7070',
    '#ff6c22',
    '#774d3b'
]

def genColor():
    indx = random.randint(0,len(arr)-1) 
    return arr[indx]