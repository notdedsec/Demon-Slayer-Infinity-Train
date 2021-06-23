
import myaa.subkt.ass.*
import myaa.subkt.tasks.*
import myaa.subkt.tasks.Mux.*
import myaa.subkt.tasks.Nyaa.*
import java.awt.Color
import java.time.*

plugins {
    id("myaa.subkt")
}

subs {
    readProperties("sub.properties", "private.properties")
    episodes(getList("episodes"))

    merge {
        from(get("dialogue")) {
            incrementLayer(10)
        }

        from(getList("typesets"))

        from(get("ending")) {
            syncTargetTime(getAs<Duration>("edsync"))
        }
    }

    mux {
        title(get("title"))

        from(get("premux")) {
            tracks {
                lang("jpn")

                if(track.type == TrackType.VIDEO){
                    name("BD 1080p x264 10bit [dedsec]")
                }

                if(track.type == TrackType.AUDIO){
                    name("qAAC 5.1ch")
                }
            }

            attachments {
                include(false)
            }
        }

        from(merge.item()) {
            tracks {
                name("Kaizoku")
                lang("eng")
                default(true)
            }
        }

        chapters(get("chapters")) {
            lang("eng")
            charset("UTF-8")
        }

        attach(get("fonts")) {
            includeExtensions("ttf", "otf")
        }

        skipUnusedFonts(true)
        out(get("muxfile"))
    }

    torrent {
        trackers(getList("tracker"))
        from(mux.item())
        out(get("torrent"))
    }

    nyaa {
        from(torrent.item())
        username(get("nyaauser"))
        password(get("nyaapass"))
        category(NyaaCategories.ANIME_ENGLISH)
        information(get("info"))
        torrentDescription(getFile("description.vm"))
        hidden(false)
    }
}
