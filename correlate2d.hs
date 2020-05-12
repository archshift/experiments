type Vec = [Double]
type Matrix = [Vec]

flatten :: [[a]] -> [a]
flatten [] = []
flatten [first] = first
flatten (first:rest) =
    first ++ (flatten rest)

--- >>> flatten [[1, 2], [3, 4]]
--- [1.0,2.0,3.0,4.0]
---

rewrap :: (Int, Int) -> Vec -> Matrix
rewrap (n, m) []
    | (n * m == 0) = []
    | otherwise    = error "dimension mismatch"

rewrap (r, c) vec =
    let (first, rest) = splitAt c vec
        matRem = rewrap (r-1, c) rest
     in first : matRem

--- >>> rewrap (2, 2) [1, 2, 3, 4]
--- [[1.0,2.0],[3.0,4.0]]
---

vfold2d :: (Double -> Double -> Double) -> Double -> Matrix -> Vec
vfold2d _ _ [] = []
vfold2d func acc mat =
    let heads = map head mat
        tails = filter (not . null) (map tail mat)
     in (foldl func acc heads) : (vfold2d func acc tails)

--- >>> vfold2d (+) 0 [[1], [2, 3], [4, 5, 6]]
--- >>> vfold2d (+) 0 [[1]]
--- [7.0,8.0,6.0]
--- [1.0]
---

dot :: Vec -> Vec -> Double
dot [] [] = 0 
dot (f1:r1) (f2:r2) = f1*f2 + dot r1 r2
dot [] (_:_) = error "dimension mismatch"
dot (_:_) [] = error "dimension mismatch"

--- >>> dot [1, 2, 3, 4] [1, 2, 3, 4]
--- 30.0
---

makeWindows' :: Vec -> Vec -> [Vec]
makeWindows' [] _ = []
makeWindows' _ [] = error "empty previous window"
makeWindows' (new:vecRest) (_:prevRest) =
    let first = prevRest ++ [new]
     in first : makeWindows' vecRest first


makeWindows :: Int -> Vec -> [Vec]
makeWindows len vec =
    let (first, rest) = splitAt len vec
     in first : (makeWindows' rest first)

paddedWindows :: Int -> Vec -> [Vec]
paddedWindows len vec =
    let hlen = quot len 2
        pad = replicate hlen 0
        paddedVec = pad ++ vec ++ pad
     in makeWindows len paddedVec


--- >>> makeWindows 2 [1, 2, 3, 4, 5, 6]
--- [[1.0,2.0],[2.0,3.0],[3.0,4.0],[4.0,5.0],[5.0,6.0]]
--- >>> paddedWindows 3 [1, 2, 3, 4, 5, 6]
--- [[0.0,1.0,2.0],[1.0,2.0,3.0],[2.0,3.0,4.0],[3.0,4.0,5.0],[4.0,5.0,6.0],[5.0,6.0,0.0]]
---

weightRowDots :: Vec -> Matrix -> Vec
weightRowDots wRow fMat =
    let wDim = length wRow
        paddedRows = map (paddedWindows wDim) fMat
        dotter = dot wRow
        rowDotter = map dotter
     in flatten (map rowDotter paddedRows)

--- >>> weightRowDots [-1, 0, 1] [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
--- [2.0,2.0,-2.0,5.0,2.0,-5.0,8.0,2.0,-8.0]
---

skips :: Int -> Int -> [Int]
skips wDim fDim =
    map (\x -> fDim * ((quot wDim 2) - x)) [0..wDim-1]

applySkip :: Int -> Vec -> Vec
applySkip skip vec =
    case compare skip 0 of
        GT -> replicate skip 0 ++ vec
        EQ -> vec
        LT -> snd (splitAt (-skip) vec)

--- >>> skips 3
--- [1,0,-1]
--- >>> applySkip 1 [1, 2, 3]
--- >>> applySkip (-1) [1, 2, 3]
--- [0.0,1.0,2.0,3.0]
--- [2.0,3.0]
---

correlate :: Matrix -> Matrix -> Matrix
correlate wt fm =
    let wDim = length (head wt)
        fDim = length (head fm)
        weightDots = map (\r -> weightRowDots r fm) wt
        skips' = skips wDim fDim
        skippedDots = map (uncurry applySkip) (zip skips' weightDots)
        overrun = vfold2d (+) 0 skippedDots
     in rewrap (fDim, fDim) (take (fDim * fDim) overrun)

--- >>> wt = [[0, 1, 0], [1, 1, 1], [0, 1, 0]]
--- >>> fm = rewrap (5, 5) [1..25]
--- >>> correlate wt fm
--- [[9.0,13.0,17.0,21.0,19.0],[25.0,35.0,40.0,45.0,39.0],[45.0,60.0,65.0,70.0,59.0],[65.0,85.0,90.0,95.0,79.0],[59.0,83.0,87.0,91.0,69.0]]
---
