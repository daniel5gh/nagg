//Load common code that includes config, then load the app logic for this page.
requirejs(['/static/common.js'], function (common) {
    requirejs(['mainpage/main1']);
});
