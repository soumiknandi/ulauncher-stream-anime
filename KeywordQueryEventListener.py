from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.item.ExtensionSmallResultItem import ExtensionSmallResultItem
from ulauncher.api.shared.action.SetUserQueryAction import SetUserQueryAction


class KeywordQueryEventListener(EventListener):

    history = None

    def on_event(self, event, extension):

        args = event.get_argument()

        # When user types anime name after search
        if "search " in str(args):

            # Get the anime name
            anime_name = str(args).replace("search ", "")

            return RenderResultListAction([
                ExtensionResultItem(
                    icon="images/icon.png",
                    name="Press enter to search " + anime_name,
                    description="Search " + anime_name,
                    on_enter=ExtensionCustomAction({
                        "action": "search_anime",
                        "anime_name": anime_name,
                        "curr_list": -1
                    }, keep_app_open=True)
                )
            ])

        # When user selects anime search option
        if "search" in str(args):
            return RenderResultListAction([
                ExtensionResultItem(
                    icon="images/icon.png",
                    name="Write the anime name you want to search",
                    description=f"Example : {extension.preferences['keyword']} search one piece",
                    on_enter=SetUserQueryAction(extension.preferences['keyword'] + " search "))
            ])

        # When user types desired episode number
        if str(args).replace("type episode number : ", "").isdigit():

            # Get episode number
            episode = str(args).replace("type episode number : ", "")
            anime = extension.get_current_anime()

            return RenderResultListAction([
                ExtensionResultItem(
                    icon="images/icon.png",
                    name=f"Open {anime.name} episode : {episode}",
                    description="Press enter to open episode",
                    on_enter=ExtensionCustomAction(
                        {
                            "action": "open_episode",
                            "episode": episode,
                        }, keep_app_open=True))
            ])

        # When user selects desired episode number
        if "type episode number :" in str(args):
            return RenderResultListAction([
                ExtensionResultItem(
                    icon="images/icon.png",
                    name="Type episode number : ",
                    on_enter=DoNothingAction())
            ])

        # When user selects history
        if "history" in str(args) or str(args).replace("history page ", "").isdigit():
            output = []

            page = str(args).replace("history page ", "")
            if not page.isdigit():
                page = 1
            elif int(page) <= 0:
                page = 1

            page = int(page)

            # Get history
            history = extension.read_history(page)

            if history is None:
                output.append(
                    ExtensionSmallResultItem(
                        icon="images/icon.png",
                        name="No history present",
                        on_enter=DoNothingAction()
                    )
                )
            else:
                anime_history = history["animes"]
                is_next = history["next"]

                if page > 1:
                    output.append(
                        ExtensionSmallResultItem(
                            icon="images/icon.png",
                            name="Previous page",
                            on_enter=SetUserQueryAction(f'{extension.preferences["keyword"]} history page {page - 1}'))
                    )

                for anime in anime_history:
                    output.append(
                        ExtensionSmallResultItem(
                            icon="images/icon.png",
                            name=f"{anime.name} ({anime.language}) ({anime.provider})",
                            on_enter=ExtensionCustomAction({
                                "action": "open_anime_history",
                                "anime": anime,
                            }, keep_app_open=True)
                        )
                    )

                # Show delete all option
                output.append(
                    ExtensionSmallResultItem(
                        icon="images/icon.png",
                        name="Delete all history",
                        on_enter=ExtensionCustomAction({
                            "action": "delete_item",
                            "delete_all": True
                        }, keep_app_open=True)
                    )
                )

                if is_next:
                    output.append(
                        ExtensionSmallResultItem(
                            icon="images/icon.png",
                            name="Next page",
                            on_enter=SetUserQueryAction(
                                f"{extension.preferences['keyword']} history page {page+1}"
                            ))
                    )

            return RenderResultListAction(output)

        # Default Options

        extension.set_up_provider(extension.preferences["provider"])

        output = []

        history = extension.read_history(1)

        # Show anime search option
        output.append(
            ExtensionResultItem(
                icon="images/icon.png",
                name="Search anime",
                description="Find anime by name",
                on_enter=SetUserQueryAction(f"{extension.preferences['keyword']} search "))
        )

        # Show anime history option
        output.append(
            ExtensionResultItem(
                icon="images/icon.png",
                name="Watch history",
                description="View your watch history",
                on_enter=SetUserQueryAction(f"{extension.preferences['keyword']} history"))
        )

        # Show continue last watched anime option
        if history is not None:
            last_anime = history["animes"][0]
            output.append(
                ExtensionResultItem(
                    icon="images/icon.png",
                    name=f"Continue watching {last_anime.name} ({last_anime.language})",
                    description=f"Open {last_anime.name} next episode : {str(int(last_anime.episode) + 1)}",
                    on_enter=ExtensionCustomAction({
                        "action": "open_episode_direcly",
                        "anime": last_anime,
                        "episode": int(last_anime.episode) + 1,
                    }, keep_app_open=True))


            )

        return RenderResultListAction(output)
