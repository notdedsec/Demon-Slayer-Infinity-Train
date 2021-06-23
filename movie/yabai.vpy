import insaneAA
import lvsfunc as lvf
import havsfunc as haf
import kagefunc as kgf
import vardefunc as vdf
import vapoursynth as vs
from cooldegrain import CoolDegrain
from adptvgrnMod import adptvgrnMod
from vsutil import depth, join, plane

core = vs.core
core.max_cache_size = 24000

exclude_range = [
    (77112, 77328), (79408, 79480), (80166, 81527), 
    (101139, 101171), (101436, 101460), (101876, 101894),
    (101943, 101975), (102017, 102040), (102077, 102125)
]

src = lvf.src(r"yabai.m2ts")
src = depth(src, 16)

descale = depth(kgf.inverse_scale(plane(src, 0), height=855, kernel='bicubic', b=1/5, c=2/5, mask_detail=True), 16)
dehalo = haf.FineDehalo(descale, rx=2.4, darkstr=0, brightstr=0.8, thmi=44)
upscale = insaneAA.rescale(dehalo, dx=1920, dy=1080)
aa = insaneAA.insaneAA(src, external_aa=upscale)
merge = join([aa, plane(src, 1), plane(src, 2)])

adaptive_mask = kgf.adaptive_grain(merge, luma_scaling=8, show_mask=True)
denoise_a = CoolDegrain(merge, thsad=64, thsadc=48, blksize=8, overlap=4)
denoise_b = CoolDegrain(merge, thsad=16, thsadc=48, blksize=8, overlap=4)
denoise = core.std.MaskedMerge(denoise_a, denoise_b, adaptive_mask)

line_mask = kgf.retinex_edgemask(denoise).std.Binarize(9999).rgvs.RemoveGrain(3).std.Inflate()
deband = vdf.deband.dumb3kdb(denoise, radius=18, threshold=44)
deband = core.std.MaskedMerge(deband, merge, line_mask)

grain = adptvgrnMod(deband, strength=0.25, size=1.15, sharp=75, static=True)
exclude = lvf.rfs(grain, src, ranges=exclude_range)

final = depth(exclude, 10)
final.set_output()
