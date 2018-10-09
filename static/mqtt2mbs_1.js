var  gettype=Object.prototype.toString

function getParam(name) {
    //构造一个含有目标参数的正则表达式对象
    var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)"); 
    //匹配目标参数
    var r = window.location.search.substr(1).match(reg);
    //返回参数值
    if (r != null) return unescape(r[2]);
    //不存在时返回null
    return null; 
}

function checkIP(value){
    console.log(value);
    if(value=="localhost"){
        // alert("你输入的IP地址有效");
        return true;
    }
    str = value.match(/(\d+)\.(\d+)\.(\d+)\.(\d+)/g);
    if (str == null){
        // alert("你输入的IP地址格式不正确");
        return false;
    }else if (RegExp.$1>224 || RegExp.$2>255 || RegExp.$3>255 || RegExp.$4>255){
        // alert("你输入的IP地址无效");
        return false;
    }else{
        // alert("你输入的IP地址有效");
        return true;
    }
}

function checkDomain(enDomain) {
	 var i;
	 var ii;
	 var aa;
	 if(enDomain == "" || enDomain == " " || enDomain.length < 4)   {
		  alert("请您输入有效的域名！");
		  return false;
		 
	}
	    var checkOK = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-0123456789|.!=+%/_: ";
	 var allValid = true;
	 for(i = 0;   i < enDomain.length;   i++)  {
		  ch = enDomain.charAt(i);
		  for (j = 0;   j < checkOK.length;   j++)
			  if (ch == checkOK.charAt(j))
				   break;
		  if (j == checkOK.length)
			  {
				   allValid = false;
				   break;
				 
			}
		 
	}
	  if(!allValid) {
		  alert("请输入有效的域名或路径！");
		  return false;
		 
	}
	    if (enDomain.length > 0)
		  {
			       ii = enDomain.indexOf(".");
                    if (ii == -1)
					  {
						   alert("有效的域名或路径中必须含有“.”和域名后缀！");
						   return false       
					}
				   
		}
	  return true;
	 
}

function check_tcp_port(value){

    str = value.match(/(\d+)/g);
    console.log(parseInt(RegExp.$1));
    if (str == null){
        // alert("端口范围1~65535");
        return false;
    }else if (1<parseInt(RegExp.$1)<65535){
        // alert("你输入的TCP端口有效");
        return true;
    }else{
        // alert("你输入的TCP端口无效");
        return false;
    }
}

function check_local_status() {
   // console.log(net_mode, bind_port);
    // 检测本地服务状态
    $.ajax({
      url: 'http://127.0.0.1:5060/mb_service_status',
      headers: {
              Accept: "application/json; charset=utf-8",
              Authorization: "Bearer 123123123"
              },
      type: 'get',
      contentType: "application/json; charset=utf-8",
      dataType:'json',
      //async:false,
      success:function(data){
          $("span.service_status").html(data.mqtt2mbs_Service);

          console.log(data.mqtt2mbs_Service);

          // console.log(index);
          if (data.mqtt2mbs_Service=="RUNNING") {
                $("span.service_status").addClass('text-success');
                $("span.service_status").removeClass('text-danger');
				$("button.start_service").addClass("hide");
				$("button.stop_service").removeClass("hide");
				$("button.stop_service").addClass("btn-danger");

			  }
          else{
                $("span.service_status").removeClass('text-success');
                $("span.service_status").addClass('text-danger');
				$("button.stop_service").addClass("hide");
				$("button.start_service").removeClass("hide");
				$("button.start_service").addClass("btn-primary");
              }

      },
      error:function(data){
            console.log("无法连接配置服务，请启动配置服务");

      }

    });

    // 检测本地服务状态
}

function check_service_config() {
    // 发送心跳

    $.ajax({
      url: '/r_config',
      headers: {
              Accept: "application/json; charset=utf-8",
              Authorization: "Bearer 123123123"
              },
      type: 'get',
      contentType: "application/json; charset=utf-8",
      dataType:'json',
      // async:false,
      // data: JSON.stringify(postinfo),
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
              if(key=="cloud"){
                  $("span.cloud_Authcode").text(val);
                }
              if(key=="log"){
                  $("span.log_level").text(val);
              }

            // console.log('键名是:'+key, '键值类型是:'+gettype.call(val));

          });

      },
      error:function(data){
          console.log(data);
      }
    });
}

function query_cloudproxy_status(proxy_item) {
    var cloud_proxy = {"proxy_stcp":proxy_item};
    // console.log(cloud_proxy);
    $.ajax({
      url: 'http://127.0.0.1:5000/cloudstatus',
      headers: {
              Accept: "application/json; charset=utf-8",
              Authorization: "Bearer 123123123"
              },
      type: 'post',
      contentType: "application/json; charset=utf-8",
      dataType:'json',
      //async:false,
      data: JSON.stringify(cloud_proxy),
      success:function(data){
        if(data){
              $.each(data,function(key,val){
                // console.log('键名是:'+key, '键值是:'+val);

                $('span#cloud_tunnel_name').html(val.name);
                $('span#this_start_time').html(val.last_start_time);
                $('span#last_Traffic_data').html(Math.round((Number(val.today_traffic_in)+Number(val.today_traffic_out))/1024) + "KB");

                if(Number(val.cur_conns)>0){
                    $('span#local_link_result').removeClass('text-danger');
                    $('span#local_link_result').addClass('text-success');
                    $('span#local_link_result').html("已连接");
                }
                else{
                    $('span#local_link_result').removeClass('text-success');
                    $('span#local_link_result').addClass('text-danger');
                    $('span#local_link_result').html("未连接");
                }

                if(val.status=="online"){
                    $('span#cloud_tunnel_status').removeClass('text-danger');
                    $('span#cloud_tunnel_status').addClass('text-success');
                    $('span#cloud_tunnel_status').html(val.status);
                }
                else{
                    $('span#cloud_tunnel_status').removeClass('text-success');
                    $('span#cloud_tunnel_status').addClass('text-danger');
                    $('span#cloud_tunnel_status').html(val.status);
                }
            });
        }
        else{

          $("div#cloud_ret_message").html("代理服务未查询到任何数据");

        }

      },
      error:function(data){
          $("div#cloud_ret_message").html("无法连接本地服务，请检查IOE隧道服务是否启动");
      }
    });
}

function check_ip_alive(ip) {
  postdata = {"ipaddr":ip}
   $.ajax({
      url: 'http://127.0.0.1:5000/ip_alive',
      headers: {
              Accept: "application/json; charset=utf-8",
              Authorization: "Bearer 123123123"
              },
      type: 'post',
      contentType: "application/json; charset=utf-8",
      dataType:'json',
      data: JSON.stringify(postdata),
      success:function(data){
        // console.log(data);
        //   console.log(data.message);
          if(data.message){
            // console.log("连接畅通");
            $("span#ping_devip_result").removeClass('text-danger')
            $("span#ping_devip_result").addClass('text-success')
            $("span#ping_devip_result").html("连接畅通");
          }
          else{
            // console.log("连接不通");
            $("span#ping_devip_result").removeClass('text-success')
            $("span#ping_devip_result").addClass('text-danger')
            $("span#ping_devip_result").html("连接不通");
          }

      },
      error:function(data){
          console.log(data);
      }
  });
}

function send_keep_alive() {
    // 发送心跳
       $.ajax({
        url: 'http://127.0.0.1:5000/keep_alive',
        headers: {
                Accept: "application/json; charset=utf-8",
                Authorization: "Bearer 123123123"
                },
        type: 'post',
        contentType: "application/json; charset=utf-8",
        dataType:'json',
        //async:false,
        data: "",
        success:function(data){
            // console.log(data);
        },
        error:function(data){
            console.log(data);
        }
      });
}

function start_local_vpn(postinfo) {
      $.ajax({
        url: 'http://127.0.0.1:5000/start',
        headers: {
                Authorization: "Bearer 123123123"
                },
        type: 'post',
        contentType: "application/json; charset=utf-8",
        dataType:'json',
        //async:false,
        data: JSON.stringify(postinfo),
        success:function(data){
				// console.log("周期检测执行结果");

				    var now = new Date();  
						exitTime = now.getTime() + 20000;
							if(!check_act_result_ret_has_start){
							  check_act_result_ret = setInterval(function(){
									check_act_result();;
							  },2000);
							  check_act_result_ret_has_start =true;
						  }
							
		    },

        error:function(data){
              $("#mes_table  tr:not(:first)").empty("");
              $("span#check_local_result").addClass('text-danger');
              $("span#check_local_result").html("无法连接本地服务，请检查freeioe_vpn_Service服务是否启动或者运行环境是否安装，如未安装，" + '<a href="/downloads/freeioe_vpn_green.rar"  class="navbar-link">点击下载</a>');
        }
      });

}

function stop_local_vpn() {
      $.ajax({
        url: 'http://127.0.0.1:5000/stop',
        headers: {
                Authorization: "Bearer 123123123"
                },
        type: 'post',
        contentType: "application/json; charset=utf-8",
        dataType:'json',
        //async:false,
        data: "",
        success:function(data){

			if(data.message){
					$("div#vpn_ret_message").removeClass("hide");
					var date = new Date();  
					var strDate = date.toLocaleString().replace(/[年月]/g,'-').replace(/[日上下午]/g,'');  
					$("div#vpn_ret_message").html(strDate+": 停止成功");
					check_local_status();
					query_cloudproxy_status(frpc_item);
					if(!check_local_status_has_start){
						check_local_status_has_start = true;
						check_local_status_ret = setInterval(function(){
						  check_local_status();
						},5000);						
					}			
			}
			else{
					$("div#vpn_ret_message").removeClass("hide");
					var date = new Date();  
					var strDate = date.toLocaleString().replace(/[年月]/g,'-').replace(/[日上下午]/g,'');  
					$("div#vpn_ret_message").html(strDate + ": 停止失败，VPN已经停止或其他原因");
			}
			


        },
        error:function(data){
            $("#mes_table  tr:not(:first)").empty("");
            $("span#check_local_result").addClass('text-danger');
            $("span#check_local_result").html("无法连接本地服务，请检查IOE隧道服务是否启动");
			$("div#vpn_ret_message").html("");
        }
      });

}

function check_gate_isbusy(sn, url, code) {
	    var postinfo = {
			"gate_sn": sn,
			"cloud_url": url,
			"auth_code": code,
		}
      $.ajax({
        url: 'http://127.0.0.1:5000/gate_isbusy',
        headers: {
                Authorization: "Bearer 123123123"
                },
        type: 'post',
        contentType: "application/json; charset=utf-8",
        dataType:'json',
        //async:false,
        data: JSON.stringify(postinfo),
        success:function(data){
				console.log(data);
				if(data.message==1){
					vpn_msg_html = "你准备操作的网关正在被其他用户使用！请关闭当前页面，稍候再试！";
					$("span.error_tips").html(vpn_msg_html);
					 $('#myModal').modal('show'); 		
				}else{
                    $("input#dev_ip").val(data.br_lan_ipv4);
                }
			
		    },

        error:function(data){
              $("#mes_table  tr:not(:first)").empty("");
              $("span#check_local_result").addClass('text-danger');
              $("span#check_local_result").html("无法连接本地服务，请检查freeioe_vpn_Service服务是否启动或者运行环境是否安装，如未安装，" + '<a href="/downloads/freeioe_vpn_green.rar"  class="navbar-link">点击下载</a>');
        }
      });

}

function check_gate_alive(sn, url, code) {
	    var postinfo = {
			"gate_sn": sn,
			"cloud_url": url,
			"auth_code": code,
		}
      $.ajax({
        url: 'http://127.0.0.1:5000/gate_alive',
        headers: {
                Authorization: "Bearer 123123123"
                },
        type: 'post',
        contentType: "application/json; charset=utf-8",
        dataType:'json',
        //async:false,
        data: JSON.stringify(postinfo),
        success:function(data){
				// console.log(data);
				if(data.message=="ONLINE"){
					$("span.gate_status_result").addClass("text-success");
					$("span.gate_status_result").removeClass("text-danger");
					$("span.gate_status_result").html(data.message);
					gate_status="ONLINE";
				}
				if(data.message=="OFFLINE"){
					$("span.gate_status_result").addClass("text-danger");
					$("span.gate_status_result").removeClass("text-success");
					$("span.gate_status_result").html(data.message);
					$(".tunnel_config").attr("disabled",true);
					$("button#start_vpn").attr("disabled",true);
					gate_status="OFFLINE";
					if(vpn_running){
						stop_local_vpn();
					}
					
				}				
		    },

        error:function(data){
              $("#mes_table  tr:not(:first)").empty("");
              $("span#check_local_result").addClass('text-danger');
              $("span#check_local_result").html("无法连接本地服务，请检查freeioe_vpn_Service服务是否启动或者运行环境是否安装，如未安装，" + '<a href="/downloads/freeioe_vpn_green.rar"  class="navbar-link">点击下载</a>');
        }
      });

}

function check_act_result() {
   $.ajax({
      url: 'http://127.0.0.1:5000/act_result',
      headers: {
              Accept: "application/json; charset=utf-8",
              Authorization: "Bearer 123123123"
              },
      type: 'get',
      contentType: "application/json; charset=utf-8",
      dataType:'json',
      success:function(data){
	  				var now = new Date(); 
					$("div#vpn_ret_message").removeClass("hide");
					var ret_mes='';
					var date = new Date();  
					var strDate = date.toLocaleString().replace(/[年月]/g,'-').replace(/[日上下午]/g,'');  
					if(data.cloud_mes){
						// console.log("cloud_mes:", data.cloud_mes);
						ret_mes = ret_mes + "平台返回消息： " + strDate + "  " + data.cloud_mes + '<br />';
						$("div#vpn_ret_message").html(ret_mes);
					}
					else{
						ret_mes = ret_mes + "平台返回消息： "+ strDate + "   空" + '<br />';
						$("div#vpn_ret_message").html(ret_mes);
					}
					if(data.gate_mes){
						// console.log("gate_mes:", data.gate_mes);
						ret_mes = ret_mes+ "网关返回消息： "  + strDate + "  " + data.gate_mes + '<br />';
						$("div#vpn_ret_message").html(ret_mes);
					}
					else{
						ret_mes = ret_mes+ "网关返回消息：" + strDate + "   空"  + '<br />';
						$("div#vpn_ret_message").html(ret_mes);					
					}
					
					if(data.vpn_mes){
					// console.log("vpn_mes:", data.vpn_mes);
						ret_mes = ret_mes + data.vpn_me + '<br />';
						$("div#vpn_ret_message").html(ret_mes);
					}
					if(data.services_mes){
						// console.log("vpn_mes:", data.services_mes);
						ret_mes = ret_mes + "本地返回消息： " + strDate + "  " + data.services_mes + '<br />';
						$("div#vpn_ret_message").html(ret_mes);

							exitTime = now.getTime() - 1;

					}
					// console.log(exitTime-now.getTime());
					if(now.getTime() > exitTime){
						// console.log("退出check_act_result");
						clearInterval(check_act_result_ret);
						check_act_result_ret_has_start=false;
						
						if(!check_local_status_has_start){
							check_local_status_has_start = true;
							check_local_status_ret = setInterval(function(){
							  check_local_status();
							},5000);						
						}

					}
		
		},
      error:function(data){
          console.log(data);
      }
  });
}

function one_key_repair() {
   $.ajax({
      url: 'http://127.0.0.1:5000/one_key_repair',
      headers: {
              Accept: "application/json; charset=utf-8",
              Authorization: "Bearer 123123123"
              },
      type: 'get',
      contentType: "application/json; charset=utf-8",
      dataType:'json',
      success:function(data){
		console.log(data);
		if(data.message){
			$("span#check_env_result").html("修复完成，重新检测运行环境……");
		}
		setTimeout("check_local_env()",5000);
		},
      error:function(data){
              $("#mes_table  tr:not(:first)").empty("");
              $("span#check_local_result").addClass('text-danger');
              $("span#check_local_result").html("无法连接本地服务，请检查freeioe_vpn_Service服务是否启动或者运行环境是否安装，如未安装，" + '<a href="/downloads/freeioe_vpn_green.rar"  class="navbar-link">点击下载</a>');
      }
  });
}

function get_logfiles() {
    // 发送心跳
       $.ajax({
        url: '/logfiles',
        headers: {
                Accept: "application/json; charset=utf-8",
                Authorization: "Bearer 123123123"
                },
        type: 'get',
        contentType: "application/json; charset=utf-8",
        dataType:'json',
        //async:false,
        data: "",
        success:function(data){

            var html_text='';
            $.each(data,function(key,val){
                // console.log(key,val);
                if(key==0){
                    html_text = html_text + '<li role="presentation" class="log_tab active" data-id="'+ val +'"><a href="#">' + val +'</a></li>'
                }else{
                    html_text = html_text + '<li role="presentation" class="log_tab" data-id="' + val + '"><a href="#">' + val +'</a></li>'
                }

            });

            $("ul.log_view_nav").html(html_text);
            if(data.length>0){
                // console.log(data[0]);
                get_logcontent(data[0]);
            }

        },
        error:function(data){
            console.log(data);
        }
      });
}

function get_logcontent(filename) {
    // 发送心跳
       $.ajax({
        url: '/log/'+filename,
        headers: {
                Accept: "application/json; charset=utf-8",
                Authorization: "Bearer 123123123"
                },
        type: 'get',
        // contentType: "application/text; charset=utf-8",
        dataType:'text',
        // async:false,
        // data: "",
        success:function(data){
            // console.log(data);
            $("div.log_title").html("当前日志："+filename);
            $("div.log_content").html('<pre>' + data + '</pre>');
            // $.each($("textarea"), function(i, n){
            //     $(n).css("height", n.scrollHeight + "px");
            // })
        },
        error:function(data){
            // console.log(data);
        }
      });
}

function cfg_monitor() {
    // 发送心跳
    $.ajax({
        url: '/cfg_change',
        headers: {
                Authorization: "Bearer 123123123"
                },
        type: 'get',
        contentType: "application/json; charset=utf-8",
        dataType:'json',
        success:function(data){
            if (data.message){
                $("span.operation_tip").html("配置更改，请重启生效！");
            }else{
                $("span.operation_tip").html("");
            }

            },
        error:function(data){

        }
      });
}