// ********** configurations **********

// 설정하지 않을 경우, 현재 갤러리 ID
var gall_id = undefined;

// 삭제할 IP 리스트
var ip_blacklist = ['118.235', '223.39']

// 새로고침 최소 주기 (단위: 초)
var interval_min = 30

// 새로고침 최대 주기 (단위: 초)
var interval_max = 600

// 새로고침 주기 증가량 (1.05=1.05배)
var interval_mul = 1.05

// 새로고침 주기 랜덤화 범위 (단위: 초) ex) min=30,rnd=30 -> 30~60초 사이
var interval_rnd = 30

// ********** configurations **********

function parseCookies() {
    var cookies = {};
    var cookieString = document.cookie;

    if (cookieString === "") {
        return cookies;
    }

    var cookieArray = cookieString.split(";");

    for (var i = 0; i < cookieArray.length; i++) {
        var cookie = cookieArray[i].trim();
        var separatorIndex = cookie.indexOf("=");
        var cookieName = decodeURIComponent(cookie.substring(0, separatorIndex));
        var cookieValue = decodeURIComponent(cookie.substring(separatorIndex + 1));
        cookies[cookieName] = cookieValue;
    }

    return cookies;
}

function DCPostTR($d, tr) {
    var $e = $d.find(tr);

    var title = $e.find('td.gall_tit > a')[0]?.textContent;
    var postId = Number.parseInt($e.find("td.gall_num")[0]?.textContent);
    var postType = $e.find('.gall_subject')[0]?.textContent
    var writer = $e.find('td.gall_writer > span.nickname')[0]?.textContent
    var writer_ip = $e.find("td.ub-writer")[0]?.getAttribute("data-ip")

    return {
        title,
        postId,
        postType,
        writer,
        writer_ip,
        check_del: () => {
            $e.find(".gall_chk > span > input")[0].checked = true
        }
    }
}
function get_posts($d) {
    var posts = $d.find("tr.ub-content")
    posts = posts.map((_, tr) => DCPostTR($d, tr))
    return posts
}
function filter_posts(posts) {
    posts = posts.filter((_, p) => ip_blacklist.includes(p.writer_ip))
    return posts
}
async function block_and_del_posts(gid, posts) {
    var nos = ''
    for (var p of posts) {
        nos += `nos[]=${p.postId}&`
    }
    nos = nos.slice(0, -1)
    nos = encodeURI(nos)

    var cookies = parseCookies()
    var ci_t = cookies["ci_c"]
    var res = await fetch("https://gall.dcinside.com/ajax/minor_manager_board_ajax/update_avoid_list", {
        "credentials": "include",
        "headers": {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin"
        },
        "referrer": `https://gall.dcinside.com/mgallery/board/lists?id=${gid}`,
        "body": `ci_t=${ci_t}&id=${gid}&${nos}&parent=&avoid_hour=6&avoid_reason=4&avoid_reason_txt=&del_chk=1&_GALLTYPE_=M`,
        "method": "POST",
        "mode": "cors"
    });
    var js = await res.json()
    return js['result'] == 'success'
}

if (gall_id == undefined) {
    if (window.location.pathname.includes('/mgallery/board/lists')) {
        var params = new URLSearchParams(window.location.search)
        gall_id = params.get('id')
    }
    else {
        gall_id = window.location.pathname.split('/')[2]
    }
}

var loops = 0;
var elapsed = 0;
var removals = 0;
var interval = interval_min
var last_time = Date.now()

var timer = setTimeout(async function main() {
    loops += 1

    var now = Date.now()
    elapsed += (now - last_time) / 1000

    var h = (elapsed / 3600).toFixed(0)
    var m = ((elapsed % 3600) / 60).toFixed(0)
    var rmpt, rmpu;
    rmpt = removals / (Math.max(elapsed, 1));
    rmpu = 's'
    if (rmpt > 0 && rmpt < 1) {
        rmpt = removals / Math.max(elapsed / 60, 1)
        rmpu = 'm'
    }
    if (rmpt > 0 && rmpt < 1) {
        rmpt = removals / Math.max(elapsed / 3600, 1)
        rmpu = 'h'
    }
    console.log(`${loops}th loops. ${h}h ${m}m elapsed. ${removals} posts removed (${rmpt.toFixed(2)}/${rmpu})`)

    var html = await fetch(`https://gall.dcinside.com/mgallery/board/lists?id=${gall_id}`, {
        headers: {
            "Referer": `https://gall.dcinside.com/board/lists?id=${gall_id}`
        }
    }).then(r => r.text())
    var parser = new DOMParser()
    var dom = parser.parseFromString(html, "text/html")
    var $d = $(dom)
    var posts = get_posts($d)
    var posts = filter_posts(posts)
    if (posts.length == 0) {
        interval = Math.min(interval * interval_mul, interval_max) + Math.random() * interval_rnd
        timer = setTimeout(main, interval * 1000)
    }
    else {
        var success = await block_and_del_posts(gall_id, posts)
        interval = interval_min
        timer = setTimeout(main, interval * 1000)
        if (success) {
            for (var p of posts) {
                console.log(`pid=${p.postId} ptype=${p.postType} title=${p.title}, writer=${p.writer}, ip=${p.writer_ip}`)
            }
            removals += posts.length
        }
        else {
            console.log(`이미 삭제되었습니다.`)
        }
    }
    console.log(`${posts.length} posts to remove. next check in ${interval.toFixed(2)} seconds`)
    last_time = Date.now()
}, 0);