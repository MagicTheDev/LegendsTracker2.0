

async def pingToMember(ctx, ping):
  ping = str(ping)
  if (ping.startswith('<@') and ping.endswith('>')):
    ping = ping[2:len(ping) - 1]

  if (ping.startswith('!')):
    ping = ping[1:len(ping)]

  try:
    member = await ctx.guild.fetch_member(ping)
    return member
  except:
    return None


async def pingToRole(ctx, ping):
    ping = str(ping)
    if (ping.startswith('<@') and ping.endswith('>')):
        ping = ping[2:len(ping) - 1]

    if (ping.startswith('&')):
        ping = ping[1:len(ping)]

    try:
      role = ctx.guild.get_role(int(ping))
      return role
    except:
        return None

async def pingToChannel(ctx, ping):
  ping = str(ping)
  if (ping.startswith('<#') and ping.endswith('>')):
    ping = ping[2:len(ping) - 1]

  try:
    channel =  ctx.guild.get_channel(int(ping))
    return channel
  except:
    return None