
  // cloud_url = "http://iot.symgrid.com";
  // auth_code = getParam('authcode');
  // gate_sn_org  = getParam('gate_sn');


$(document).ready(function() {

    check_local_status();
    check_service_config();
    // check_tunnel_mode();
    // check_local_status();
    //
    //
    // var t1 = setTimeout("query_cloudproxy_status(frpc_item)",3000);
    // var t2 = setTimeout("check_local_env()",2000);
    //
    // check_local_status_ret = setInterval(function(){
    //   check_local_status();
    //   },5000);
    //
    // setInterval(function(){	  check_gate_alive(gate_sn, cloud_url, auth_code);	  },5000);
    //
    // check_cloud_status_ret = setInterval(function(){
    // 	query_cloudproxy_status(frpc_item);
    //   },20000);



// 一键修复按钮
    $("body").on("click", "a.one_key_repair", function () {
        one_key_repair();
    });
// 一键修复按钮


// 测试按钮
    $("button#mytest").click(function () {
        // var dev_ip = $("input#dev_ip").val();
        // check_act_result();
        // check_gate_alive(gate_sn, cloud_url, auth_code);
        // one_key_repair();


    });
// 测试按钮

// 选择按钮--云端状态-----开始
    $("button#cloud").click(function () {
        query_cloudproxy_status(frpc_item);
    });
// 选择按钮--云端状态-----结束


// 选择按钮--网络模式-----开始
    $("button#bridge").click(function () {
        net_mode = "bridge";
        bind_port = "665";
        frpc_item = gate_sn + "_" + net_mode;
        // console.log(net_mode);
        $("input#tap_ip").val("192.168.0.33");
        $("span#vn_ipaddr").html("虚拟网卡IP:");
        $("span#vn_netmask").html("虚拟网卡netmask:");
        $("button#bridge").addClass("btn-primary active");
        $("button#router").removeClass("btn-primary active");
    });

    $("button#router").click(function () {
        net_mode = "router";
        bind_port = "666";
        frpc_item = gate_sn + "_" + net_mode;
        // console.log(net_mode);
        $("input#tap_ip").val("192.168.0.0");
        $("span#vn_ipaddr").html("现场子网地址:");
        $("span#vn_netmask").html("现场子网netmask:");
        $("button#bridge").removeClass("btn-primary active");
        $("button#router").addClass("btn-primary active");
    });
// 选择按钮--网络模式-----结束

// 选择按钮--协议-----开始
    $("button#protocol_tcp").click(function () {
        net_protocol = "tcp";
        // console.log(net_protocol);
        $("button#protocol_tcp").addClass("btn-primary active");
        $("button#protocol_kcp").removeClass("btn-primary active");
    });

    $("button#protocol_kcp").click(function () {
        net_protocol = "kcp";
        // console.log(net_protocol);
        $("button#protocol_tcp").removeClass("btn-primary active");
        $("button#protocol_kcp").addClass("btn-primary active");
    });
// 选择按钮--协议-----结束


// 配置按钮--mbserv修改-----开始
    $("button.mbserv_modify").click(function () {

        $(this).addClass("hide");
        $(this).prevAll().removeClass("hide");
        $(this).nextAll().removeClass("hide");
        $("input.mbserv_input").removeClass("hide");
        $('span.mbserv_text').addClass('hide')
    });

// 配置按钮--mbserv修改------结束

// 配置按钮--mbserv保存-----开始
    $("button.mbserv_save").click(function () {
        var aa = new Object();
        var mbServ_cfg = {"mbServ": aa};
        $("input.mbserv_input").each(function(k, v){
		// let this = $(this);
		    console.log(k, $(this).val());
		    if(k==0){
		        if(checkIP($(this).val())){
		            aa.host=$(this).val()
                }else{
		            return false
                }
            }
            if(k==1){
		        if(check_tcp_port($(this).val())){
		            aa.port=$(this).val()
                }else{
		            return false
                }
            }
        });
        console.log(mbServ_cfg);


      $.ajax({
        url: '/w_config',
        headers: {
                Authorization: "Bearer 123123123"
                },
        type: 'post',
        contentType: "application/json; charset=utf-8",
        dataType:'json',
        //async:false,
        data: JSON.stringify(mbServ_cfg),
        success:function(data){
                          $.each(data,function(key,val){
                          if(key=="mbServ"){
                              $("span.mbserv_host").text(val[0]);
                              $("span.mbserv_port").text(val[1]);
                          }
                          if(key=="redis"){
                              $("span.redis_host").text(val[0]);
                              $("span.redis_port").text(val[1]);
                          }
                          if(key=="mqtt"){
                              $("span.mqtt_host").text(val[0]);
                              $("span.mqtt_port").text(val[1]);
                              $("span.mqtt_keepalive").text(val[2]);
                              $("span.mqtt_user").text(val[3]);
                          }
                          if(key=="log"){
                              $("span.log_level").text(val);
                          }
                      });
                            $("button.mbserv_save").addClass("hide");
                            $("button.mbserv_cancel").addClass("hide");
                            $("button.mbserv_modify").removeClass("hide");
                            $("span.mbserv_text").removeClass("hide");
                            $("input.mbserv_input").addClass("hide");

            },

        error:function(data){
                            $("button.mbserv_save").addClass("hide");
                            $("button.mbserv_cancel").addClass("hide");
                            $("button.mbserv_modify").removeClass("hide");
                            $("span.mbserv_text").removeClass("hide");
                            $("input.mbserv_input").addClass("hide");
        }
      });

});

// 配置按钮--mbserv保存------结束

// 配置按钮--mbserv取消-----开始
$("button.mbserv_cancel").click(function () {
    $(this).addClass("hide");
    $("button.mbserv_save").addClass("hide");
    $("button.mbserv_modify").removeClass("hide");
    $("span.mbserv_text").removeClass("hide");
    $("input.mbserv_input").addClass("hide");
});

// 配置按钮--mbserv取消------结束



// 配置按钮--mqtt修改-----开始
    $("button.mqtt_modify").click(function () {

        $(this).addClass("hide");
        $(this).prevAll().removeClass("hide");
        $(this).nextAll().removeClass("hide");
        $("input.mqtt_input").removeClass("hide");
        $("div.mqtt_pwd").removeClass("hide");
        $('span.mqtt_text').addClass('hide')
    });

// 配置按钮--mqtt修改------结束

// 配置按钮--mqtt保存-----开始
    $("button.mqtt_save").click(function () {

        $("input.mqtt_input").each(function(k, v){
		// let this = $(this);
		    console.log(k, $(this).val());
		    if(k==0){
		        if(!checkIP($(this).val())){
		            checkDomain($(this).val());
                }
            }
            if(k==1){
		        check_tcp_port($(this).val());
            }
            if(k==2){
                console.log((10<parseInt($(this).val())<600));
		        if (!(10<parseInt($(this).val())<600)){
                    alert("有效范围10~600");
                };
            }
            if(k==3){

            }
            if(k==4){

            }
        });
        return

    });

// 配置按钮--mqtt保存------结束

// 配置按钮--mqtt取消-----开始
$("button.mqtt_cancel").click(function () {
    $(this).addClass("hide");
    $("button.mqtt_save").addClass("hide");
    $("button.mqtt_modify").removeClass("hide");
    $("span.mqtt_text").removeClass("hide");
    $("input.mqtt_input").addClass("hide");
    $("div.mqtt_pwd").addClass("hide");
});

// 配置按钮--mqtt取消------结束


// 配置按钮--redis修改-----开始
    $("button.redis_modify").click(function () {

        $(this).addClass("hide");
        $(this).prevAll().removeClass("hide");
        $(this).nextAll().removeClass("hide");
        $("input.redis_input").removeClass("hide");
        $('span.redis_text').addClass('hide');
        $("div.redis_pwd").removeClass("hide");
    });

// 配置按钮--redis修改------结束

// 配置按钮--redis保存-----开始
    $("button.redis_save").click(function () {

        $("input.redis_input").each(function(k, v){
		    if(k==0){
		        if(!checkIP($(this).val())){
		            checkDomain($(this).val());
                }
            }
            if(k==1){
		        check_tcp_port($(this).val());
            }
            if(k==2){

            }
        });

        return



    });

// 配置按钮--redis保存------结束

// 配置按钮--redis取消-----开始
$("button.redis_cancel").click(function () {
    $(this).addClass("hide");
    $("button.redis_save").addClass("hide");
    $("button.redis_modify").removeClass("hide");
    $("span.redis_text").removeClass("hide");
    $("input.redis_input").addClass("hide");
    $("div.redis_pwd").addClass("hide");
});

// 配置按钮--redis取消------结束

// 配置按钮--log修改-----开始
    $("button.log_modify").click(function () {

        $(this).addClass("hide");
        $(this).prevAll().removeClass("hide");
        $(this).nextAll().removeClass("hide");
        $("input.log_input").removeClass("hide");
        $('span.log_text').addClass('hide')
    });

// 配置按钮--log修改------结束


// 配置按钮--log保存-----开始
    $("button.log_save").click(function () {
        var log_level = $("input.log_input").val();
        // console.log(log_level);
        if(log_level){
            var log_cfg = {"log": {"level":log_level}};
          $.ajax({
            url: '/w_config',
            headers: {
                    Authorization: "Bearer 123123123"
                    },
            type: 'post',
            contentType: "application/json; charset=utf-8",
            dataType:'json',
            //async:false,
            data: JSON.stringify(log_cfg),
            success:function(data){
                              $.each(data,function(key,val){
                              if(key=="mbServ"){
                                  $("span.mbserv_host").text(val[0]);
                                  $("span.mbserv_port").text(val[1]);
                              }
                              if(key=="redis"){
                                  $("span.redis_host").text(val[0]);
                                  $("span.redis_port").text(val[1]);
                              }
                              if(key=="mqtt"){
                                  $("span.mqtt_host").text(val[0]);
                                  $("span.mqtt_port").text(val[1]);
                                  $("span.mqtt_keepalive").text(val[2]);
                                  $("span.mqtt_user").text(val[3]);
                              }
                              if(key=="log"){
                                  $("span.log_level").text(val);
                              }
                          });
                                $("button.log_save").addClass("hide");
                                $("button.log_cancel").addClass("hide");
                                $("button.log_modify").removeClass("hide");
                                $("span.log_text").removeClass("hide");
                                $("input.log_input").addClass("hide");

                },

            error:function(data){
                    console.log(data);
                        $(this).addClass("hide");
                        $("button.log_cancel").addClass("hide");
                        $("button.log_modify").removeClass("hide");
                        $("span.log_text").removeClass("hide");
                        $("input.log_input").addClass("hide");
            }
          });
        }

    });

// 配置按钮--log保存------结束

// 配置按钮--log取消-----开始
$("button.log_cancel").click(function () {
    $(this).addClass("hide");
    $("button.log_save").addClass("hide");
    $("button.log_modify").removeClass("hide");
    $("span.log_text").removeClass("hide");
    $("input.log_input").addClass("hide");
});

// 配置按钮--log取消------结束

// 导航按钮--服务状态-----开始
    $("button.nav_service_status").click(function () {
        console.log("#######");
        $(this).addClass("active");
        $(this).prevAll().removeClass("active");
        $(this).nextAll().removeClass("active");
        $("div.log_view").addClass("hide");
        $("div.service_config").removeClass("hide");
    });

// 导航按钮--服务状态------结束

// 导航按钮--日志查看-----开始
    $("button.nav_log_view").click(function () {
        console.log("@@@@@@");
        get_logfiles();
        $(this).addClass("active");
        $(this).prevAll().removeClass("active");
        $(this).nextAll().removeClass("active");
        $("div.service_pannel").addClass("hide");
        $("div.log_view").removeClass("hide");
    });

// 导航按钮--日志查看------结束

// 导航按钮--映射点表-----开始
    $("button.nav_tag_map").click(function () {
        console.log("*************");
        $(this).addClass("active");
        $(this).prevAll().removeClass("active");
        $(this).nextAll().removeClass("active");
    });

// 导航按钮--映射点表------结束

// 日志浏览--日志切换-----开始

 $("body").on("click","li.log_tab",function(){
            console.log($(this).attr('data-id'));
            $(this).addClass("active");
            $(this).prevAll().removeClass("active");
            $(this).nextAll().removeClass("active");
            get_locontent($(this).attr('data-id'));
    });

// 日志浏览--日志切换------结束

// 刷新按钮-------开始
    $("button.refresh_status").click(function () {
        // console.log("刷新状态");
        var patt1 = $("button.nav_log_view").attr("class");
        if(patt1.indexOf("active")<0){
            check_service_config();
            check_local_status();
        }else{
            check_local_status();
            get_logfiles()
        }

    });

// 刷新按钮--------结束


// 启动按钮-------开始
    $("button.start_service").click(function () {
        // console.log("刷新状态");
        $("span.service_status").html("正在启动……");
        $.ajax({
            url: '/mb_service_start',
            headers: {
                    Authorization: "Bearer 123123123"
                    },
            type: 'post',
            contentType: "application/json; charset=utf-8",
            dataType:'json',
            success:function(data){
                check_local_status();
                if (!(data.mqtt2mbs_Service=="RUNNING")){
                    $("span.operation_tip").html("无法启动，请查看日志了解原因");
                }else{
                    $("span.operation_tip").html("");
                }

                },
            error:function(data){

            }
          });

    });

// 启动按钮--------结束

// 停止按钮-------开始
    $("button.stop_service").click(function () {
        // console.log("刷新状态");
        $("span.service_status").html("正在停止……")
        $.ajax({
            url: '/mb_service_stop',
            headers: {
                    Authorization: "Bearer 123123123"
                    },
            type: 'post',
            contentType: "application/json; charset=utf-8",
            dataType:'json',
            success:function(data){
                check_local_status();
                $("span.operation_tip").html("")
                },
            error:function(data){

            }
          });

    });

// 停止按钮--------结束

// 重启按钮-------开始
    $("button.restart_service").click(function () {
        // console.log("刷新状态");
        $("span.service_status").html("正在重启……");
        $.ajax({
            url: '/mb_service_restart',
            headers: {
                    Authorization: "Bearer 123123123"
                    },
            type: 'post',
            contentType: "application/json; charset=utf-8",
            dataType:'json',
            success:function(data){
                check_local_status();
                if (!(data.mqtt2mbs_Service=="RUNNING")){
                    $("span.operation_tip").html("无法启动，请查看日志了解原因");
                }else{
                    $("span.operation_tip").html("");
                }
                },
            error:function(data){

            }
          });

    });

// 重启按钮--------结束
});