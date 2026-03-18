"""命令行入口"""

import time

import click


@click.group()
def main():
    """RuntimeFlow — 桌面操作录制与回放工具"""
    pass


@main.command()
@click.argument("name")
def record(name):
    """录制桌面操作"""
    from datetime import datetime
    from runtimeflow.environment import capture_environment
    from runtimeflow.recorder import Recorder
    from runtimeflow.storage import save_skill
    from runtimeflow.models import Flow

    click.echo("录制即将开始，3秒后开始捕获，按 F9 停止")
    for i in range(3, 0, -1):
        click.echo(f"  {i}...")
        time.sleep(1)

    env = capture_environment()
    recorder = Recorder()
    recorder.start()
    click.echo("正在录制... 按 F9 停止")
    try:
        while recorder.is_recording():
            time.sleep(0.1)
    except KeyboardInterrupt:
        recorder.stop()

    events = recorder.get_events()
    duration = events[-1].timestamp_ms if events else 0
    flow = Flow(
        name=name,
        events=events,
        environment=env,
        created_at=datetime.now().isoformat(),
        duration_ms=duration,
    )
    filepath = save_skill(flow)
    click.echo(f"\n录制完成！")
    click.echo(f"  名称: {name}")
    click.echo(f"  事件数: {flow.event_count}")
    click.echo(f"  时长: {flow.duration_ms:.0f}ms")
    click.echo(f"  保存至: {filepath}")


@main.command()
@click.argument("name")
def play(name):
    """回放已录制的操作"""
    from runtimeflow.environment import validate_environment
    from runtimeflow.player import Player
    from runtimeflow.storage import load_skill

    flow = load_skill(name)
    click.echo(f"已加载 skill: {flow.name} ({flow.event_count} 个事件)")
    click.echo("请切换到目标窗口，10秒后开始回放，按 F10 中断")
    for i in range(10, 0, -1):
        click.echo(f"  {i}...")
        time.sleep(1)

    passed, diffs = validate_environment(flow.environment)
    if not passed:
        click.echo("环境校验未通过：")
        for d in diffs:
            click.echo(f"  - {d}")
        raise SystemExit(1)

    click.echo("环境校验通过")

    player = Player()
    player.play(flow.events)
    try:
        while player.is_playing():
            time.sleep(0.1)
    except KeyboardInterrupt:
        player.stop()
    click.echo("回放完成！")


@main.command("list")
def list_skills_cmd():
    """列出所有已保存的 skill"""
    from runtimeflow.storage import list_skills

    skills = list_skills()
    if not skills:
        click.echo("暂无已保存的 skill")
        return

    click.echo(f"共 {len(skills)} 个 skill：")
    for s in skills:
        click.echo(
            f"  {s['name']}  |  事件: {s['event_count']}  "
            f"|  时长: {s['duration_ms']:.0f}ms  |  {s['created_at']}"
        )


@main.command()
@click.argument("name")
def info(name):
    """查看 skill 详情"""
    from runtimeflow.storage import load_skill

    flow = load_skill(name)
    env = flow.environment
    click.echo(f"名称: {flow.name}")
    click.echo(f"创建时间: {flow.created_at}")
    click.echo(f"事件数: {flow.event_count}")
    click.echo(f"时长: {flow.duration_ms:.0f}ms")
    click.echo(f"环境:")
    click.echo(f"  平台: {env.platform}")
    click.echo(f"  分辨率: {env.screen_width}x{env.screen_height}")
    click.echo(f"  DPI: {env.dpi_scale}")
    click.echo(f"  窗口: {env.window_title}")
    click.echo(f"  位置: ({env.window_x}, {env.window_y}) {env.window_width}x{env.window_height}")
