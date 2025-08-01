# Copyright (c) Microsoft. All rights reserved.


from unittest.mock import MagicMock

from azure.ai.agents.models import (
    MessageDelta,
    MessageDeltaChunk,
    MessageDeltaImageFileContent,
    MessageDeltaImageFileContentObject,
    MessageDeltaTextContent,
    MessageDeltaTextContentObject,
    MessageDeltaTextFileCitationAnnotation,
    MessageDeltaTextFileCitationAnnotationObject,
    MessageDeltaTextFilePathAnnotation,
    MessageDeltaTextFilePathAnnotationObject,
    MessageDeltaTextUrlCitationAnnotation,
    MessageDeltaTextUrlCitationDetails,
    MessageImageFileContent,
    MessageImageFileDetails,
    MessageTextContent,
    MessageTextDetails,
    MessageTextFileCitationAnnotation,
    MessageTextFileCitationDetails,
    MessageTextFilePathAnnotation,
    MessageTextFilePathDetails,
    MessageTextUrlCitationAnnotation,
    MessageTextUrlCitationDetails,
    RequiredFunctionToolCall,
    RunStep,
    RunStepBingCustomSearchToolCall,
    RunStepBingGroundingToolCall,
    RunStepDeltaFunction,
    RunStepDeltaFunctionToolCall,
    RunStepDeltaToolCallObject,
    RunStepFunctionToolCall,
    RunStepFunctionToolCallDetails,
    ThreadMessage,
)

from semantic_kernel.agents.azure_ai.agent_content_generation import (
    generate_annotation_content,
    generate_bing_grounding_content,
    generate_code_interpreter_content,
    generate_function_call_content,
    generate_function_result_content,
    generate_message_content,
    generate_streaming_annotation_content,
    generate_streaming_code_interpreter_content,
    generate_streaming_function_content,
    generate_streaming_message_content,
    get_function_call_contents,
    get_message_contents,
)
from semantic_kernel.contents.annotation_content import AnnotationContent
from semantic_kernel.contents.chat_message_content import ChatMessageContent
from semantic_kernel.contents.file_reference_content import FileReferenceContent
from semantic_kernel.contents.function_call_content import FunctionCallContent
from semantic_kernel.contents.function_result_content import FunctionResultContent
from semantic_kernel.contents.image_content import ImageContent
from semantic_kernel.contents.streaming_annotation_content import StreamingAnnotationContent
from semantic_kernel.contents.streaming_file_reference_content import StreamingFileReferenceContent
from semantic_kernel.contents.streaming_text_content import StreamingTextContent
from semantic_kernel.contents.text_content import TextContent
from semantic_kernel.contents.utils.author_role import AuthorRole


def test_get_message_contents_all_types():
    chat_msg = ChatMessageContent(role=AuthorRole.USER, content="")
    chat_msg.items.append(TextContent(text="hello world"))
    chat_msg.items.append(ImageContent(uri="http://example.com/image.png"))
    chat_msg.items.append(FileReferenceContent(file_id="file123"))
    chat_msg.items.append(FunctionResultContent(id="func1", result={"a": 1}))
    results = get_message_contents(chat_msg)
    assert len(results) == 4
    assert results[0]["type"] == "text"
    assert results[1]["type"] == "image_url"
    assert results[2]["type"] == "image_file"
    assert results[3]["type"] == "text"


def test_generate_message_content_text_and_image():
    thread_msg = ThreadMessage(
        content=[],
        role="user",
    )

    image = MessageImageFileContent(image_file=MessageImageFileDetails(file_id="test_file_id"))

    text = MessageTextContent(
        text=MessageTextDetails(
            value="some text",
            annotations=[
                MessageTextFileCitationAnnotation(
                    text="text",
                    file_citation=MessageTextFileCitationDetails(file_id="file_id", quote="some quote"),
                    start_index=0,
                    end_index=9,
                ),
                MessageTextFilePathAnnotation(
                    text="text again",
                    file_path=MessageTextFilePathDetails(file_id="file_id_2"),
                    start_index=1,
                    end_index=10,
                ),
                MessageTextUrlCitationAnnotation(
                    text="text",
                    url_citation=MessageTextUrlCitationDetails(title="some title", url="http://example.com"),
                    start_index=1,
                    end_index=10,
                ),
            ],
        )
    )

    thread_msg.content = [image, text]
    step = RunStep(id="step_id", run_id="run_id", thread_id="thread_id", agent_id="agent_id")
    out = generate_message_content("assistant", thread_msg, step)
    assert len(out.items) == 5
    assert isinstance(out.items[0], FileReferenceContent)
    assert isinstance(out.items[1], TextContent)
    assert isinstance(out.items[2], AnnotationContent)
    assert isinstance(out.items[3], AnnotationContent)
    assert isinstance(out.items[4], AnnotationContent)

    assert out.items[0].file_id == "test_file_id"

    assert out.items[1].text == "some text"

    assert out.items[2].file_id == "file_id"
    assert out.items[2].quote == "text"
    assert out.items[2].start_index == 0
    assert out.items[2].end_index == 9
    assert out.items[2].citation_type == "file_citation"

    assert out.items[3].file_id == "file_id_2"
    assert out.items[3].quote == "text again"
    assert out.items[3].start_index == 1
    assert out.items[3].end_index == 10
    assert out.items[3].citation_type == "file_path"

    assert out.items[4].url == "http://example.com"
    assert out.items[4].quote == "text"
    assert out.items[4].start_index == 1
    assert out.items[4].end_index == 10
    assert out.items[4].title == "some title"
    assert out.items[4].citation_type == "url_citation"

    assert out.metadata["step_id"] == "step_id"
    assert out.role == AuthorRole.USER


def test_generate_annotation_content():
    message_text_file_path_ann = MessageTextFilePathAnnotation(
        text="some text",
        file_path=MessageTextFilePathDetails(file_id="file123"),
        start_index=0,
        end_index=9,
    )

    message_text_file_citation_ann = MessageTextFileCitationAnnotation(
        text="some text",
        file_citation=MessageTextFileCitationDetails(file_id="file123"),
        start_index=0,
        end_index=9,
    )

    for fake_ann in [message_text_file_path_ann, message_text_file_citation_ann]:
        out = generate_annotation_content(fake_ann)
        assert out.file_id == "file123"
        assert out.quote == "some text"
        assert out.start_index == 0
        assert out.end_index == 9


def test_generate_streaming_message_content_text_annotations():
    message_delta_image_file_content = MessageDeltaImageFileContent(
        index=0,
        image_file=MessageDeltaImageFileContentObject(file_id="image_file"),
    )

    MessageDeltaTextFileCitationAnnotation, MessageDeltaTextFilePathAnnotation

    message_delta_text_content = MessageDeltaTextContent(
        index=0,
        text=MessageDeltaTextContentObject(
            value="some text",
            annotations=[
                MessageDeltaTextFileCitationAnnotation(
                    index=0,
                    file_citation=MessageDeltaTextFileCitationAnnotationObject(file_id="file123", quote="some text"),
                    start_index=0,
                    end_index=9,
                    text="some text",
                ),
                MessageDeltaTextFilePathAnnotation(
                    index=0,
                    file_path=MessageDeltaTextFilePathAnnotationObject(file_id="file123"),
                    start_index=1,
                    end_index=10,
                    text="some text",
                ),
                MessageDeltaTextUrlCitationAnnotation(
                    index=0,
                    url_citation=MessageDeltaTextUrlCitationDetails(
                        title="some title",
                        url="http://example.com",
                    ),
                    start_index=2,
                    end_index=11,
                ),
            ],
        ),
    )

    delta = MessageDeltaChunk(
        id="chunk123",
        delta=MessageDelta(role="user", content=[message_delta_image_file_content, message_delta_text_content]),
    )

    out = generate_streaming_message_content("assistant", delta)
    assert out is not None
    assert out.content == "some text"
    assert len(out.items) == 5
    assert out.items[0].file_id == "image_file"
    assert isinstance(out.items[0], StreamingFileReferenceContent)
    assert isinstance(out.items[1], StreamingTextContent)
    assert isinstance(out.items[2], StreamingAnnotationContent)

    assert out.items[2].file_id == "file123"
    assert out.items[2].quote == "some text"
    assert out.items[2].start_index == 0
    assert out.items[2].end_index == 9
    assert out.items[2].citation_type == "file_citation"

    assert isinstance(out.items[3], StreamingAnnotationContent)
    assert out.items[3].file_id == "file123"
    assert out.items[3].quote == "some text"
    assert out.items[3].start_index == 1
    assert out.items[3].end_index == 10
    assert out.items[3].citation_type == "file_path"

    assert isinstance(out.items[4], StreamingAnnotationContent)
    assert out.items[4].url == "http://example.com"
    assert out.items[4].title == "some title"
    assert out.items[4].start_index == 2
    assert out.items[4].end_index == 11
    assert out.items[4].citation_type == "url_citation"


def test_generate_annotation_content_url_annotation_without_indices():
    ann = MessageTextUrlCitationAnnotation(
        text="url text",
        url_citation=MessageTextUrlCitationDetails(title="", url="http://ex.com"),
        start_index=None,
        end_index=None,
    )
    out = generate_annotation_content(ann)
    assert out.file_id is None
    assert out.url == "http://ex.com"
    assert out.title == ""  # preserve empty title
    assert out.quote == "url text"
    assert out.start_index is None
    assert out.end_index is None
    assert out.citation_type == "url_citation"


def test_generate_streaming_annotation_content_url_quote_none_and_missing_indices():
    ann = MessageDeltaTextUrlCitationAnnotation(
        index=0,
        url_citation=MessageDeltaTextUrlCitationDetails(title="", url="http://ex.com"),
        start_index=None,
        end_index=None,
    )
    out = generate_streaming_annotation_content(ann)
    assert out.file_id is None
    assert out.url == "http://ex.com"
    assert out.title == ""
    assert out.quote is None  # no .text on URL annotation
    assert out.start_index is None
    assert out.end_index is None
    assert out.citation_type == "url_citation"


def test_generate_streaming_message_content_text_only_no_annotations():
    delta = MessageDeltaChunk(
        id="c1",
        delta=MessageDelta(
            role="assistant",
            content=[
                MessageDeltaTextContent(
                    index=0,
                    text=MessageDeltaTextContentObject(value="just text", annotations=[]),
                )
            ],
        ),
    )
    out = generate_streaming_message_content("assistant", delta)
    assert out.content == "just text"
    assert len(out.items) == 1
    assert isinstance(out.items[0], StreamingTextContent)
    assert out.items[0].text == "just text"


def test_generate_annotation_content_empty_title_and_url_only():
    ann = MessageTextUrlCitationAnnotation(
        text=None,
        url_citation=MessageTextUrlCitationDetails(title=None, url="http://empty.com"),
        start_index=5,
        end_index=10,
    )
    out = generate_annotation_content(ann)
    assert out.quote is None  # allow None text
    assert out.url == "http://empty.com"
    assert out.title is None  # allow None title
    assert out.start_index == 5
    assert out.end_index == 10


def test_generate_streaming_annotation_content_file_and_citation_have_text():
    file_ann = MessageDeltaTextFileCitationAnnotation(
        index=0,
        file_citation=MessageDeltaTextFileCitationAnnotationObject(file_id="f1", quote="q1"),
        start_index=2,
        end_index=4,
        text="q1",
    )
    out = generate_streaming_annotation_content(file_ann)
    assert out.file_id == "f1"
    assert out.quote == "q1"
    assert out.citation_type == "file_citation"
    assert out.start_index == 2
    assert out.end_index == 4


def test_generate_streaming_function_content_with_function():
    step_details = RunStepDeltaToolCallObject(
        tool_calls=[
            RunStepDeltaFunctionToolCall(
                index=0, id="tool123", function=RunStepDeltaFunction(name="some_func", arguments={"arg": "val"})
            )
        ]
    )

    out = generate_streaming_function_content("my_agent", step_details)
    assert out is not None
    assert len(out.items) == 1
    assert isinstance(out.items[0], FunctionCallContent)
    assert out.items[0].function_name == "some_func"
    assert out.items[0].arguments == "{'arg': 'val'}"


def test_get_function_call_contents_no_action():
    run = type("ThreadRunFake", (), {"required_action": None})()
    fc = get_function_call_contents(run, {})
    assert fc == []


def test_get_function_call_contents_submit_tool_outputs():
    fake_function = MagicMock()
    fake_function.name = "test_function"
    fake_function.arguments = {"arg": "val"}

    fake_tool_call = MagicMock(spec=RequiredFunctionToolCall)
    fake_tool_call.id = "tool_id"
    fake_tool_call.function = fake_function

    run = MagicMock()
    run.required_action.submit_tool_outputs.tool_calls = [fake_tool_call]

    function_steps = {}
    fc = get_function_call_contents(run, function_steps)

    assert len(fc) == 1
    assert fc[0].id == "tool_id"
    assert fc[0].name == "test_function"
    assert fc[0].arguments == {"arg": "val"}


def test_generate_function_call_content():
    fcc = FunctionCallContent(id="id123", name="func_name", arguments={"x": 1})
    msg = generate_function_call_content("my_agent", [fcc])
    assert len(msg.items) == 1
    assert msg.role == AuthorRole.ASSISTANT


def test_generate_function_result_content():
    step = FunctionCallContent(id="123", name="func_name", arguments={"k": "v"})

    tool_call = RunStepFunctionToolCall(
        id="123",
        function=RunStepFunctionToolCallDetails({
            "name": "func_name",
            "arguments": '{"k": "v"}',
            "output": "result_data",
        }),
    )
    msg = generate_function_result_content("my_agent", step, tool_call)
    assert len(msg.items) == 1
    assert msg.items[0].result == "result_data"
    assert msg.role == AuthorRole.TOOL


def test_generate_code_interpreter_content():
    msg = generate_code_interpreter_content("my_agent", "some_code()")
    assert msg.content == "some_code()"
    assert msg.metadata["code"] is True


def test_generate_streaming_code_interpreter_content_no_calls():
    step_details = type("Details", (), {"tool_calls": None})
    assert generate_streaming_code_interpreter_content("my_agent", step_details) is None


def test_generate_bing_grounding_content():
    """Test generate_bing_grounding_content with RunStepBingGroundingToolCall."""
    bing_grounding_tool_call = RunStepBingGroundingToolCall(
        id="call_gvgTmSL4hgdxWP4O7LLnwMlt",
        bing_grounding={
            "requesturl": "https://api.bing.microsoft.com/v7.0/search?q=search",
            "response_metadata": "{'market': 'en-US', 'num_docs_retrieved': 5, 'num_docs_actually_used': 5}",
        },
    )

    msg = generate_bing_grounding_content("my_agent", bing_grounding_tool_call)

    assert len(msg.items) == 1
    assert msg.role == AuthorRole.ASSISTANT
    assert isinstance(msg.items[0], FunctionCallContent)
    assert msg.items[0].id == "call_gvgTmSL4hgdxWP4O7LLnwMlt"
    assert msg.items[0].name == "bing_grounding"
    assert msg.items[0].function_name == "bing_grounding"
    assert msg.items[0].arguments["requesturl"] == "https://api.bing.microsoft.com/v7.0/search?q=search"
    assert msg.items[0].arguments["response_metadata"] == (
        "{'market': 'en-US', 'num_docs_retrieved': 5, 'num_docs_actually_used': 5}"
    )


def test_generate_bing_custom_search_content():
    """Test generate_bing_grounding_content with RunStepBingCustomSearchToolCall."""
    bing_custom_search_tool_call = RunStepBingCustomSearchToolCall(
        id="call_abc123def456ghi",
        bing_custom_search={
            "query": "semantic kernel python",
            "custom_config_id": "config_123",
            "search_results": "{'num_results': 10, 'top_result': 'Microsoft Semantic Kernel'}",
        },
    )

    msg = generate_bing_grounding_content("my_agent", bing_custom_search_tool_call)

    assert len(msg.items) == 1
    assert msg.role == AuthorRole.ASSISTANT
    assert isinstance(msg.items[0], FunctionCallContent)
    assert msg.items[0].id == "call_abc123def456ghi"
    assert msg.items[0].name == "bing_custom_search"
    assert msg.items[0].function_name == "bing_custom_search"
    assert msg.items[0].arguments["query"] == "semantic kernel python"
    assert msg.items[0].arguments["custom_config_id"] == "config_123"
    assert msg.items[0].arguments["search_results"] == (
        "{'num_results': 10, 'top_result': 'Microsoft Semantic Kernel'}"
    )
