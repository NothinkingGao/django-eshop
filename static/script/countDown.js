function countDown(endtime){
      var starttime = new Date(endtime);
      setInterval(function () {
        var nowtime = new Date();
        var time = starttime - nowtime;
        var day = parseInt(time / 1000 / 60 / 60 / 24);
        var hour = parseInt(time / 1000 / 60 / 60 % 24);
        var minute = parseInt(time / 1000 / 60 % 60);
        var seconds = parseInt(time / 1000 % 60);
        document.getElementById('timespan').innerHTML=(day + "天" + hour + "小时" + minute + "分钟" + seconds + "秒");
      }, 1000);
}