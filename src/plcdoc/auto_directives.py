from typing import List

from sphinx.ext.autodoc.directive import (
    AutodocDirective,
    DummyOptionSpec,
    DocumenterBridge,
)
from sphinx.ext.autodoc.directive import (
    process_documenter_options,
    parse_generated_content,
)
from sphinx.util.docutils import Reporter
from sphinx.util import logging

logger = logging.getLogger(__name__)


class PlcAutodocDirective(AutodocDirective):
    """Base class for auto-directives for the PLC domain.

    It extends the ``autodoc`` extension auto-directive base class.

    It works as a dispatcher of Documenters. It invokes a Documenter on running.
    After the processing, it parses and returns the generated content by
    Documenter. The directive itself doesn't modify the content.

    The exact type is extracted from the full directive name and the appropriate
    documenter is selected based on it.
    """

    option_spec = DummyOptionSpec()
    has_content = True
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True

    def run(self) -> List:
        reporter: Reporter = self.state.document.reporter

        try:
            source, lineno = reporter.get_source_and_line(self.lineno)  # type: ignore
        except AttributeError:
            source, lineno = (None, None)

        logger.debug(f"[plcdoc] {source}:{lineno}: input:\n{self.block_text}")

        # Look up target Documenter
        objtype = self.name.replace("auto", "")  # Remove prefix from directive name
        doccls = self.env.app.registry.documenters[objtype]

        # Process the options with the selected documenter's option_spec
        try:
            documenter_options = process_documenter_options(
                doccls, self.config, self.options
            )
        except (KeyError, ValueError, TypeError) as exc:
            # an option is either unknown or has a wrong type
            logger.error(
                "An option to %s is either unknown or has an invalid value: %s"
                % (self.name, exc),
                location=(source, lineno),
            )
            return []

        # Generate output
        params = DocumenterBridge(
            self.env, reporter, documenter_options, lineno, self.state
        )
        documenter = doccls(params, self.arguments[0])
        documenter.generate(more_content=self.content)
        if not params.result:
            return []

        logger.debug("[plcdoc] output:\n%s", "\n".join(params.result))

        # Record all filenames as dependencies -- this will at least partially make
        # automatic invalidation possible
        for fn in params.record_dependencies:
            self.state.document.settings.record_dependencies.add(fn)

        result = parse_generated_content(self.state, params.result, documenter)
        return result
