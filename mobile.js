function DCPostTR(tr) {
    var $e = $(tr);
    return {
        get_postId: () => {
            return Number.parseInt($e.find("td.gall_num")[0].textContent)
        },
        get_writer_ip: () => {
            return $e.find("td.ub-writer")[0].getAttribute("data-ip")
        },
        check_del: () => {
            $e.find(".gall_chk > span > input")[0].checked = true
        }
    }
}
function get_posts() {
    var posts = $("tr.ub-content")
    posts = posts.map((_, tr) => DCPostTR(tr))
    return posts
}
function filter_posts(posts) {
    posts = posts.filter((_, p) => ip_blacklist.includes(p.get_writer_ip()))
    return posts
}
function block_and_del_posts(posts) {
    for (var p of posts) {
        p.check_del()
    }
    $("div.useradmin_btnbox > button:nth-child(3)").click()
    $("#avoid_pop_avoid_hour6").click()
    $("#avoid_pop_avoid_reason_4").click()
    $("#avoid_pop > div > div.btn_box > button").click()
}

var ip_blacklist = ['118.238', '223.39']
posts = get_posts()
posts = filter_posts(posts)
block_and_del_posts(posts)

